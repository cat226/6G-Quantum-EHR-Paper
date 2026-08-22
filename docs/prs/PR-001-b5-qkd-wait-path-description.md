# PR-001 — Fix B5 QKD Wait-Path Simulation

<!--
Copy-paste-ready GitHub PR description.
Everything below is a verified fact recorded during Task 8.5.
Full write-up: docs/prs/PR-001-b5-qkd-wait-path.md
-->

## Summary

Makes `wait_timeout_seconds` operational for the B5 adaptive baseline. The
adaptive controller's bounded wait was never executed during a simulation
run, so B5 always fell back to PQC-only in the degraded QKD band instead of
waiting for the pool to replenish. Three-line behavioural fix across two
modules, plus 10 regression tests.

No cryptography is modified. B1–B4 are unchanged.

## Problem

`wait_timeout_seconds`, configured in `config/pilot.yaml` and part of the
adaptive policy since Task 6, had no effect on behaviour.

The controller has a degraded band (`pool_min_wait <= fraction <
pool_min_hybrid`) in which B5 should wait briefly for the QKD pool to
refill and use HYBRID if it recovers. That wait never happened: no
simulated time passed, the pool never replenished, the post-wait re-check
saw the same fraction it had just read, and the result was always
`PQC_ONLY`.

The failure was silent and self-concealing — the decision was still
recorded as `waited=True` with `wait_seconds=wait_timeout_seconds`, so raw
logs reported waits that never occurred, of a duration that never elapsed,
for a recovery path that could not succeed.

## Root Cause

`AdaptiveController.select_mode()` performs its bounded wait only when a
`wait_fn` is injected — deliberate, to keep the controller decoupled from
the simulation engine. `B5Adaptive.establish_session_key()` called it
without one:

```python
decision = self._controller.select_mode(pool, criticality)   # no wait_fn
```

With `wait_fn=None` the wait is a no-op and the method falls through to
`PQC_ONLY`. No test caught it: the controller's own unit tests inject a
`wait_fn` explicitly, so they exercised a path the running system never
took.

The obvious fix — `yield env.timeout(seconds)` — was not available.
`establish_session_key()` is synchronous (no `yield` anywhere in
`src/baselines/`, `src/adaptive/`, or `src/crypto/`); only
`device_process()` in the simulator is a SimPy generator. Making the wait
yield would have required converting all five baselines to generators.

## Solution

The QKD pool carries its own clock, advanced by explicit `pool.tick()`
calls that the harness keeps in lockstep with SimPy. Since the pool is the
only state that evolves with simulated time, **advancing the pool is the
bounded wait.**

1. **Inject the pool's clock** — `select_mode(pool, criticality, wait_fn=pool.tick)`.
   `QKDPool.tick()` is already a no-op during an outage, so waiting through
   an outage correctly yields no replenishment, with no special-casing.
2. **Report the wait** — `SessionResult.wait_seconds: float = 0.0`.
   Additive with a default, so B1–B4 are untouched.
3. **Keep SimPy in lockstep** — the harness advances
   `env.timeout(gap + result.wait_seconds)` and charges `wait_ms` to
   `key_establishment_ms` and `end_to_end_ms`. The pool is not ticked twice
   for the same interval.

The controller, its API, all policy thresholds, and B1–B4 are unchanged.

**Exactly one behaviour changes:** B5 in the degraded band, when the pool
recovers within the bounded wait, now reaches HYBRID instead of falling
back.

| Baseline | Condition | Before | After |
|---|---|---|---|
| B5 | QKD available | `adaptive_hybrid` | unchanged |
| **B5** | **degraded, recovers in wait** | **`pqc_only`** | **`adaptive_hybrid`** |
| B5 | degraded, timeout | `pqc_only` | unchanged (wait now elapses and is measured) |
| B5 | QKD unavailable | `pqc_only` | unchanged |
| B5 | emergency, degraded | no wait | unchanged |
| B4 | unavailable or degraded | fails | unchanged |

## Validation

Environment: Python 3.12.3, liboqs 0.16.0 (commit `8979276`), per
`docs/environment_manifest.md`.

**Test suite — 60/60 passed**, 0 failed, 0 skipped, 0 errors. The original
50 Task 8 tests are unmodified; none weakened, skipped, or deleted.

**Validation gate — 8/8 PASS** (`experiments/validate_phase17.py`, run
against a clean output directory).

**Four-scenario B4/B5 verification:**

```
SCENARIO 1: QKD fully available
  B4: success=True  mode=static_hybrid    B5: adaptive_hybrid  wait=0.0s
SCENARIO 2: QKD unavailable
  B4: success=False                       B5: pqc_only         wait=0.0s
SCENARIO 3: degraded, recovers during wait
  B4: success=False                       B5: adaptive_hybrid  wait=1.0s
SCENARIO 4: degraded, no recovery
  B4: success=False                       B5: pqc_only         wait=1.0s
```

Scenario 3 is the case this PR repairs. B4 falls back to PQC in no scenario.

**Reproducibility** — 3 devices × 12 transactions, seed 555, congested
network (2% loss), run twice:

```
transactions per run: 36 / 36
deterministic-field mismatches: 0
mode distribution: {ADAPTIVE_HYBRID: 15, PQC_ONLY: 21}
transactions that took the bounded wait: 21
```

**Cryptographic construction unchanged**, verified against an independent
reference implementation — byte-identical:

```
reference : cbfa7d275632a3a515ed563a99d56d35d777a62a7b46daf1c411820d248ca3f7
produced  : cbfa7d275632a3a515ed563a99d56d35d777a62a7b46daf1c411820d248ca3f7
```

ML-KEM-768, ML-DSA-65, AES-256-GCM, HKDF, and the hybrid KDF construction
(`IKM = QKD || ML-KEM` → HKDF-Extract → HKDF-Expand, L=32) are all
untouched. No file under `src/crypto/` is modified. The security claim
remains an engineering-level key combination with no compositional proof
claimed.

## Research Impact

This is a **simulation-correctness fix, not a research contribution** — it
implements behaviour the adaptive policy already specified, and introduces
no new mechanism.

It matters because without it the pilot would measure the wrong system:

- **Fallback frequency** was biased upward by construction — every
  degraded-band transaction counted as a fallback, since recovery during
  the wait was unreachable.
- **Latency** omitted the bounded wait entirely, so B5's distribution was
  missing the tail the wait produces.
- **QKD availability**, the primary independent variable, had its effect on
  B5 partly muted at exactly the intermediate levels where the pool
  oscillates through the degraded band.
- **The B4/B5 comparison** understated B5's ability to *retain* hybrid
  security under transient degradation, showing only that it survives
  outages B4 does not.

`wait_timeout_seconds` is now a live parameter. **Pilot results produced
after this fix are not comparable to any produced before it.**

## Limitations

- **The wait is modelled as pool advancement, not clock suspension.**
  Correct within the existing time model, but it does not block other
  simulated devices — concurrent devices are independent SimPy processes
  sharing the pool as the contended resource. Waits contending with one
  another would be a design change beyond this fix.
- **F6 — append-mode metrics output (not fixed here).**
  `MetricsCollector` opens output files in append mode by design.
  Re-running a pilot cell into an existing `results/raw/` directory
  silently double-counts that cell's transactions — no error, no warning,
  just inflated `n_transactions`. **Task 9 must use a fresh output
  directory per run**, and raw output should be checked for duplicate
  `transaction_id` values before aggregation. Tracked in `eab916e` and
  `docs/implementation_notes.md` Part III.
- **`sessions_buffer=20` makes the degraded band arrive late** — roughly 16
  draws before the fraction falls below `pool_min_hybrid`. Short cells may
  never exercise the wait band; pilot cells should be sized accordingly.
- Between-baseline hypothesis testing remains unimplemented, deferred until
  real pilot data exists.
- **The pilot has not been run.** No research results exist.

## Testing

10 new regression tests in `tests/test_b5_wait_path.py`:

| Test | Asserts |
|---|---|
| A `..._recovers_during_wait_selects_hybrid` | degraded + recovery → HYBRID |
| B `..._does_not_recover_falls_back_to_pqc` | degraded + outage → PQC_ONLY; pool unchanged |
| C `test_c_zero_wait_timeout_falls_back_immediately` | `wait_timeout=0` → immediate fallback |
| C2 `test_c2_wait_timeout_changes_the_outcome_all_else_equal` | identical inputs, differing only in `wait_timeout`, reach different modes |
| D `test_d_b4_does_not_gain_a_wait_or_a_fallback` | B4 fails; `wait_seconds == 0` |
| D2 `test_d2_b4_and_b5_still_diverge_under_the_degraded_condition` | same pool: B4 fails, B5 recovers |
| E `test_e_wait_advances_simulated_time_not_wall_clock` | 30 simulated seconds elapse in < 5 s real |
| E2 `test_e2_emergency_transactions_still_skip_the_wait` | emergency never waits |
| F `test_f_wait_path_is_deterministic_across_identical_runs` | identical decision sequences |
| — `test_simulator_advances_simpy_clock_by_the_wait_interval` | SimPy lockstep; wait charged to latency |

Tests A, C2, D2 and the simulator test **fail against the pre-fix code**.
Test E fails if the wait is ever implemented with `time.sleep()`. All
assert observable behaviour — selected mode, pool level, simulated elapsed
time, success/failure — rather than internal plumbing. The simulator test
carries an explicit non-vacuity guard, because an early draft passed
trivially by never reaching the wait band.

**To run:**

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt
# build liboqs at the commit pinned in docs/environment_manifest.md
pytest tests/ -v
python experiments/validate_phase17.py    # use a clean output directory
```

## Files Changed

3 files, +416 / −4:

- `src/baselines/baselines.py` (+17 / −1) — `wait_seconds` field; inject `wait_fn=pool.tick`; report on both B5 return paths
- `src/simulation/simulator.py` (+14 / −3) — advance SimPy by the wait; charge it to latency
- `tests/test_b5_wait_path.py` (+385) — new regression tests

Commit: `21f3099` — *Fix adaptive QKD wait-path simulation*
