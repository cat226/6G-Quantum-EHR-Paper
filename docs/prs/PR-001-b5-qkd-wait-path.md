# PR-001 — Fix B5 QKD Wait-Path Simulation

| | |
|---|---|
| **Branch** | `claude/pensive-bohr-1rdrrp` |
| **Fix commit** | `21f3099` — *Fix adaptive QKD wait-path simulation* |
| **Baseline commit** | `732b0c8` — *Add validated Task 8 research implementation* |
| **Scope** | B5 adaptive bounded-wait simulation only |
| **Status** | Validated; awaiting review |

This PR documents **only** the B5 wait-path fix. The environment manifest
(`fdb2636`) and the F6 finding (`eab916e`) are separate commits and are
not part of this change, though F6 is summarised below because it affects
how the pilot must be run.

---

## Problem

`wait_timeout_seconds` — a configured parameter in `config/pilot.yaml`
and part of the adaptive policy since Task 6 — had **no effect on
simulation behaviour**. It was inert.

The adaptive controller defines three bands over the QKD pool's fill
fraction:

| Band | Condition | Intended behaviour |
|---|---|---|
| Available | `fraction >= pool_min_hybrid` (0.3) | HYBRID immediately |
| **Degraded** | `pool_min_wait <= fraction < pool_min_hybrid` | **Wait up to `wait_timeout_seconds`; use HYBRID if the pool recovers, otherwise fall back** |
| Unavailable | `fraction < pool_min_wait` (0.1) | PQC_ONLY immediately, no wait |

The degraded band is the entire reason the wait exists. In practice the
bounded wait never happened during a simulation run: no simulated time
passed, the pool never replenished, the post-wait re-check observed the
same fraction it had just read, and the decision was **always**
`PQC_ONLY`.

The failure was silent, and worse than a plain no-op, because the
decision was still *recorded* as having waited:

```python
return ControllerDecision(
    mode=Mode.PQC_ONLY,
    state=ControllerState.PQC_FALLBACK,
    waited=True,                                    # never actually waited
    wait_seconds=self._thresholds.wait_timeout_seconds,   # never elapsed
    pool_fraction_at_decision=fraction_after,       # identical to `fraction`
)
```

Raw logs would therefore have reported waits that did not occur, of a
duration that never elapsed, for a recovery path that could not succeed.
Nothing in the test suite covered this, because the controller's own unit
tests inject a wait function explicitly and so exercised a path the
running system never took.

## Root Cause

Two facts combined.

**1. `select_mode()` only waits when a `wait_fn` is injected.**

```python
if fraction >= self._thresholds.pool_min_wait:
    # Degraded but not exhausted: bounded wait for replenishment.
    if wait_fn is not None:
        wait_fn(self._thresholds.wait_timeout_seconds)
    fraction_after = pool.available_fraction()
```

This design is deliberate and correct: it keeps the controller decoupled
from the simulation engine, per Task 8 Phase 3's interface discipline.

**2. `B5Adaptive` never injected one.**

```python
decision = self._controller.select_mode(pool, criticality)   # no wait_fn
```

With `wait_fn=None` the call is a no-op, `fraction_after == fraction`,
the fraction is by definition below `pool_min_hybrid` (that is what put
it in the degraded band), and the method falls through to `PQC_ONLY`.

**Why the obvious fix was not available.** The natural implementation —
have the wait `yield env.timeout(seconds)` — is impossible here without a
redesign. `Baseline.establish_session_key()` is an ordinary synchronous
method; there is no `yield` anywhere in `src/baselines/`, `src/adaptive/`,
or `src/crypto/`. Only `device_process()` in `src/simulation/simulator.py`
is a SimPy generator. Making the wait yield would have required
converting the whole call chain — and therefore all five baselines — to
generators.

The time model already in use resolves this. SimPy is the clock, but the
QKD pool carries **its own clock**, advanced by explicit `pool.tick(seconds)`
calls that the harness keeps in lockstep with `env.timeout()`. Since the
pool is the only state that evolves with simulated time, **advancing the
pool is the bounded wait.**

## Fix

Three changes. The controller, its API, all policy thresholds, and
baselines B1–B4 are untouched.

**1. `pool.tick` injection** (`src/baselines/baselines.py`)

```python
decision = self._controller.select_mode(pool, criticality, wait_fn=pool.tick)
```

`QKDPool.tick()` accrues key material at the configured generation rate
and is **already a no-op during an outage**, so waiting through an outage
correctly yields no replenishment with no special-casing.

**2. `SessionResult.wait_seconds`** (`src/baselines/baselines.py`)

```python
wait_seconds: float = 0.0
```

Additive, with a default, so B1–B4 construct `SessionResult` exactly as
before. B5 populates it from `decision.wait_seconds` on both the success
and failure return paths. This is what lets the harness learn how much
simulated time the wait consumed.

**3. SimPy advancement and latency accounting**
(`src/simulation/simulator.py`)

```python
wait_ms = result.wait_seconds * 1000.0
...
key_establishment_ms=result.total_establishment_ms + wait_ms,
end_to_end_ms=result.total_establishment_ms + wait_ms + net_latency_ms,
...
gap = 0.05
qkd_pool.tick(gap)
yield env.timeout(gap + result.wait_seconds)
```

The pool was already ticked for the wait interval inside
`establish_session_key()`, so it is deliberately **not** ticked for it
again — pool time and simulation time advance by the same total. The wait
is charged to key-establishment latency, so a transaction that waits is
measured as slower, which is the point.

**Timestamp convention (unchanged, worth knowing when reading raw logs).**
`timestamp=env.now` is recorded *before* `yield env.timeout(...)`, so a
timestamp is a transaction's **start** time. This predates this PR — the
inter-transaction gap was likewise never included in a transaction's own
timestamp. A transaction's own wait therefore surfaces in the *next*
transaction's timestamp, while being charged in full to its own
`key_establishment_ms`.

## Behavioral Change

| Baseline | Condition | Before | After |
|---|---|---|---|
| **B5** | QKD available | `adaptive_hybrid` | `adaptive_hybrid` *(unchanged)* |
| **B5** | **Degraded, recovers during wait** | **`pqc_only`** | **`adaptive_hybrid`** |
| **B5** | Degraded, no recovery before timeout | `pqc_only` | `pqc_only` *(unchanged, but the wait now genuinely elapses and is charged to latency)* |
| **B5** | QKD unavailable | `pqc_only` | `pqc_only` *(unchanged)* |
| **B5** | Emergency, degraded | `pqc_only`, no wait | `pqc_only`, no wait *(unchanged — emergency still skips the wait)* |
| **B4** | QKD unavailable or degraded | **fails** | **fails** *(unchanged — no wait, no fallback)* |
| **B1–B4** | any | unchanged | unchanged |

Exactly one behaviour changed: **B5 in the degraded band when the pool
recovers within the bounded wait.** That case now reaches HYBRID instead
of falling back. Everything else is preserved.

Observed, from the four-scenario verification run:

```
SCENARIO 1: QKD fully available
  B4: success=True  mode=static_hybrid    state=-
  B5: success=True  mode=adaptive_hybrid  state=qkd_available    wait=0.0s

SCENARIO 2: QKD unavailable (outage, pool empty)
  B4: success=False mode=-                state=-
  B5: success=True  mode=pqc_only         state=qkd_unavailable  wait=0.0s

SCENARIO 3: QKD degraded, recovers during bounded wait
  B4: success=False mode=-                state=-
  B5: success=True  mode=adaptive_hybrid  state=qkd_available    wait=1.0s

SCENARIO 4: QKD degraded, no recovery before timeout
  B4: success=False mode=-                state=-
  B5: success=True  mode=pqc_only         state=pqc_fallback     wait=1.0s
```

Scenario 3 is the case this PR repairs. B4 falls back to PQC in no
scenario.

## Validation

All figures below are recorded outputs, not estimates. Environment:
Python 3.12.3, liboqs 0.16.0 (commit `8979276ad1eb008215aa78a3c56b3649f604bbb1`),
per `docs/environment_manifest.md`.

### Test suite — 60/60

```
60 passed in 0.18s
```

0 failed, 0 skipped, 0 errors.

| File | Tests |
|---|---|
| `test_adaptive_controller.py` | 6 |
| `test_authentication.py` | 3 |
| `test_hybrid_kdf.py` | 7 |
| `test_integration_scenarios.py` | 6 |
| `test_pqc.py` | 7 |
| `test_qkd_pool.py` | 9 |
| `test_workload_network_metrics.py` | 12 |
| **`test_b5_wait_path.py`** *(new)* | **10** |

The original 50 Task 8 tests are unmodified — none weakened, skipped, or
deleted.

### 10 new regression tests

| # | Test | Asserts |
|---|---|---|
| A | `test_a_degraded_pool_that_recovers_during_wait_selects_hybrid` | degraded + recovery → HYBRID |
| B | `test_b_degraded_pool_that_does_not_recover_falls_back_to_pqc` | degraded + outage → PQC_ONLY; pool level unchanged |
| C | `test_c_zero_wait_timeout_falls_back_immediately` | `wait_timeout=0` → immediate fallback; pool not advanced |
| C2 | `test_c2_wait_timeout_changes_the_outcome_all_else_equal` | identical inputs differing only in `wait_timeout` reach different modes |
| D | `test_d_b4_does_not_gain_a_wait_or_a_fallback` | B4 fails; `wait_seconds == 0` |
| D2 | `test_d2_b4_and_b5_still_diverge_under_the_degraded_condition` | same degraded pool: B4 fails, B5 recovers |
| E | `test_e_wait_advances_simulated_time_not_wall_clock` | 30 simulated seconds elapse; < 5 s real time |
| E2 | `test_e2_emergency_transactions_still_skip_the_wait` | emergency never waits; pool untouched |
| F | `test_f_wait_path_is_deterministic_across_identical_runs` | identical decision sequences; non-vacuity guard |
| — | `test_simulator_advances_simpy_clock_by_the_wait_interval` | end-to-end SimPy lockstep; wait charged to `key_establishment_ms` |

Tests A, C2, D2 and the simulator test **fail against the pre-fix code**.
Test E specifically fails if the wait is ever implemented with
`time.sleep()`. Per the review guidance, these assert observable outcomes
— selected mode, pool level, simulated elapsed time, success/failure —
not internal plumbing.

### Validation gate — 8/8

```
[PASS] 1. Smoke test (all modules import and instantiate)
[PASS] 2+3. Full unit + integration test suite (pytest)
[PASS] 4. Single end-to-end EHR transaction
[PASS] 5. Single transaction for every baseline (B1-B5)
[PASS] 6. Forced QKD outage (pool depleted under outage)
[PASS] 7. Forced fallback (B5 under outage -> PQC_ONLY)
[PASS] 8. Reproducibility check (same seed, twice)
```

`experiments/validate_phase17.py` prints "7 passed" because checks 2 and
3 share a single `check()` call — this matches the Task 8 baseline output
exactly. All eight numbered checks pass. The gate must be run against a
clean output directory (see F6).

### Reproducibility

3 devices × 12 transactions, seed 555, congested network (2% packet
loss), `wait_timeout_seconds=0.5`, run twice:

```
transactions per run: 36 / 36
deterministic-field mismatches: 0
mode distribution: {'KeySource.ADAPTIVE_HYBRID': 15, 'KeySource.PQC_ONLY': 21}
controller states:  {'qkd_available': 15, 'pqc_fallback': 21}
transactions that took the bounded wait: 21
```

Compared fields: transaction id, payload bytes, mode used, controller
state, success, timestamp, communication overhead. 21 transactions
exercised the wait path, so the check is not vacuous.

## Cryptographic Scope

**This PR modifies no cryptography.** Explicitly unchanged:

- **ML-KEM-768** — `src/crypto/pqc.py` untouched
- **ML-DSA-65** — `src/crypto/pqc.py` untouched
- **AES-256-GCM** — `src/crypto/classical.py` untouched
- **HKDF** — `src/crypto/hybrid.py` untouched
- **The hybrid KDF construction** — untouched:

```
IKM         = QKD_secret || ML-KEM_shared_secret
PRK         = HKDF-Extract(salt, IKM)
session_key = HKDF-Expand(PRK, info, 32)
```

Verified after the fix against an independent reference implementation of
the construction — byte-identical:

```
reference : cbfa7d275632a3a515ed563a99d56d35d777a62a7b46daf1c411820d248ca3f7
produced  : cbfa7d275632a3a515ed563a99d56d35d777a62a7b46daf1c411820d248ca3f7
```

Also re-confirmed: concatenation order is QKD-first (reversing changes
the key); context is bound via HKDF's `info`, not the IKM; HKDF uses
SHA-256 with a 32-byte output; AES-256-GCM round-trips with a 12-byte
nonce; and the liboqs build exposes only `('ML-KEM-768',)` /
`('ML-DSA-65', 'ML-DSA-65-extmu')`, so no substitute algorithm path
exists.

The security claim is unchanged and unstrengthened: an **engineering-level
key combination**, with no compositional security proof claimed for this
QKD+PQC instantiation. It remains pinned in code as
`src.crypto.hybrid.SECURITY_CLAIM`.

## Research Relevance

This is a **simulation-correctness fix, not a research contribution.** It
implements behaviour the adaptive policy already specified in Task 6; it
introduces no new mechanism, and nothing here should be presented as
novel in the manuscript.

Its importance is that without it, the pilot would have measured the
wrong system. Four consequences:

**Fallback frequency** — the headline metric for B5. Every degraded-band
transaction previously counted as a fallback, because recovery-during-wait
was unreachable. Fallback frequency was therefore biased upward by
construction, and the bias grows with time spent in the degraded band —
exactly the region the QKD-availability sweep is designed to probe.

**Latency** — the wait cost nothing. A bounded wait is a deliberate
latency-for-security trade, and it was invisible in the measurements. B5's
latency distribution was missing the very tail the bounded wait produces,
which is also the reason the aggregator uses bootstrap CIs rather than
assuming normality.

**QKD availability** — the primary independent variable. Its effect on B5
was partly muted: intermediate availability levels, where the pool
oscillates through the degraded band, are precisely where the wait matters
most and where the pre-fix code diverged most from the intended policy.

**The B4/B5 comparison** — the project's central contrast. B4 and B5 are
meant to differ in that B5 can adapt where B4 cannot. Pre-fix, B5's
adaptation was strictly cruder than designed: an immediate fallback rather
than a bounded attempt to preserve the hybrid. The comparison would still
have shown B5 surviving outages that B4 does not, but it would have
understated B5's ability to *retain* hybrid security under transient
degradation — which is the more interesting claim.

`wait_timeout_seconds` is now a live parameter. Pilot results produced
after this fix are not comparable to any produced before it.

## F6 Operational Finding

Documented separately in `eab916e` and in `docs/implementation_notes.md`
Part III; repeated here because it governs how the pilot must be run.

`MetricsCollector` opens its output file in **append mode** (`"a"`), which
is intentional — the collector is designed to be append-friendly so a run
need not be held in memory. The consequence: **re-running an experiment
into an existing output directory appends to the previous run's file
instead of replacing it.**

This surfaced concretely during Task 8.5. `validate_phase17.py` writes to
a fixed `/tmp/phase17_validation` path; running it a second time made
check 4 fail with *"expected exactly 1 transaction, got 2"*. The
implementation was fine — the script is simply not idempotent. Clearing
the directory restored 8/8.

**For Task 9 this is a data-integrity risk, not an inconvenience.**
`run_pilot.py` uses the same collector and derives its filename from the
experiment id, which is deterministic per cell. Re-running a cell after an
interruption, a crash, or a parameter tweak would silently double-count
that cell's transactions — no error, no warning, just inflated
`n_transactions` and a distorted distribution feeding the aggregates.

Not fixed in this PR: the append semantics are deliberate, so changing
them is a design decision rather than a defect repair. Before the pilot,
adopt one of:

- write each run into a **fresh output directory** (simplest, no code change);
- have the runner refuse to start when the target `.jsonl` already exists;
- make the collector truncate, accepting the loss of append-resume.

Whichever is chosen, check the pilot's raw output for duplicate
`transaction_id` values before aggregating.

## Files Changed

Commit `21f3099` — 3 files, **+416 / −4**:

| File | Change | Description |
|---|---|---|
| `src/baselines/baselines.py` | +17 / −1 | `SessionResult.wait_seconds` field; inject `wait_fn=pool.tick`; report `wait_seconds` on both B5 return paths |
| `src/simulation/simulator.py` | +14 / −3 | Advance SimPy by `gap + result.wait_seconds`; charge `wait_ms` to `key_establishment_ms` and `end_to_end_ms` |
| `tests/test_b5_wait_path.py` | +385 / −0 | New — 10 regression tests |

Not modified by this PR: `src/adaptive/controller.py`, any file under
`src/crypto/`, `config/pilot.yaml`, `requirements.txt`, and the original
50 tests.

## Review Checklist

- [x] **B4/B5 distinction preserved** — B4 untouched; fails in scenarios 2, 3, 4; `test_d`, `test_d2`, and the original `test_b4_vs_b5_diverge_under_outage_the_critical_distinction` all pass
- [x] **No wall-clock waiting** — no `time.sleep()` anywhere in the codebase; `test_e` asserts 30 simulated seconds elapse in under 5 s of real time
- [x] **Simulated time correctly advances** — pool clock and SimPy clock advance by the same total; verified end-to-end by `test_simulator_advances_simpy_clock_by_the_wait_interval`
- [x] **Cryptographic construction unchanged** — no file under `src/crypto/` modified; derivation verified byte-identical to an independent reference
- [x] **60/60 tests pass** — 0 failed, 0 skipped, 0 errors
- [x] **8/8 validation passes** — from a clean output directory
- [x] **Reproducibility verified** — 36/36 transactions, 0 deterministic-field mismatches, 21 waits exercised
- [x] **No pilot results generated** — `results/raw/` and `results/processed/` contain only `.gitkeep`; all validation output written outside the repository

---

## Reviewer notes

Two things worth a reviewer's attention:

1. **The wait is modelled as pool advancement, not as clock suspension.**
   This is correct within the existing time model — the pool is the only
   time-evolving state — but it means the wait does not block other
   simulated devices. Concurrent devices are independent SimPy processes
   and each advances its own timeline; they share the pool, which is the
   contended resource. If a future extension needs waits to contend with
   one another, that is a design change beyond this fix.

2. **`sessions_buffer=20` makes the degraded band arrive late.** With a
   5120-bit pool and 256 bits per session, roughly 16 draws are needed
   before the fraction falls below `pool_min_hybrid`. Short cells may
   never reach the wait band at all. This caught out the first draft of
   the simulator test, which was silently vacuous until a non-vacuity
   guard was added. Worth checking that the pilot's cells are long enough
   to exercise the band they are meant to probe.
