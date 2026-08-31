# Pilot Analysis Notes

**Source:** `results/raw/pilot/` — 150 files, 757,500 transaction records
(commit `56ebb2d`), summarized by `experiments/analyze_pilot.py` into
`results/processed/pilot_summary.csv` (30 rows — one per (baseline, QKD
availability, device count) cell, pooling all 5 repetitions per cell).

**Status: descriptive statistics only.** No between-baseline hypothesis
testing has been run (Mann-Whitney U remains deferred,
`docs/implementation_notes.md` Part II §6). No figures exist yet. Nothing
here is a manuscript-ready finding — this is the record of what the pilot
data actually shows, so it can be checked, not asserted from memory.

**Scope reminder** (see `docs/scope_and_claims.md`): every timing below
was measured on the simulation host (x86-64; Python 3.12.3, liboqs
0.16.0 — `docs/environment_manifest.md`). None of it characterizes any
embedded or IoMT device.

---

## 1. Internal consistency check: communication overhead

Before trusting any latency number, the overhead-bytes figures were
cross-checked against the primitive sizes `docs/implementation_notes.md`
Part II §3 recorded as measured directly from this liboqs build
(ML-KEM-768 pk=1184/ct=1088, ML-DSA-65 sig=3309). Every baseline's
observed `communication_overhead_bytes_mean` matches the value computed
by hand from those sizes and the baseline's own code path, **exactly**,
constant across every QKD availability level and device count:

| Baseline | Observed (bytes) | Computed from code | Composition |
|---|---|---|---|
| B1 | 96 | 96 | X25519 pk (32) + Ed25519 sig (64) |
| B2 | 5,581 | 5,581 | ML-KEM pk+ct (2,272) + ML-DSA sig (3,309) |
| B3 | 3,309 | 3,309 | ML-DSA sig only (QKD exchange bytes not counted, by design) |
| B4 | 5,581 | 5,581 | Same PQC part as B2 |
| B5 | 8,890 | 8,890 | PQC (2,272) + mode-sync sig (3,309) + session sig (3,309) |

B5's overhead is **identical whether it resolves HYBRID or PQC_ONLY** —
both paths run the same PQC exchange and the same two signature round
trips (mode-sync, session-establish); only the QKD draw differs, and QKD
material isn't counted toward `communication_overhead_bytes` (matching
B4's convention). This is a property of the code, confirmed here, not an
artifact of this run.

## 2. B5's key-establishment latency is dominated by the bounded wait, not by cryptography

This is the clearest pattern in the data, and it is a direct, expected
consequence of the Task 8.5 wait-path fix (commit `21f3099`) — this is
the first full run where that fix's effect is visible at scale.

| QKD availability | Device count | `key_establishment_ms` mean | 95% CI | `fallback_frequency` |
|---|---|---|---|---|
| 1.0 | 10 | 0.438 | [0.428, 0.449] | 0.000 |
| 1.0 | 1000 | 0.432 | [0.431, 0.433] | 0.000 |
| 0.5 | 10 | 32.889 | [30.782, 34.900] | 0.032 |
| 0.5 | 1000 | 45.583 | [45.460, 45.707] | 0.047 |
| 0.0 | 10 | 40.236 | [38.432, 42.145] | 0.850 |
| 0.0 | 1000 | 47.877 | [47.783, 47.969] | 0.999 |

At full availability, B5's key-establishment cost (~0.43 ms) is
comparable to B4's (~0.26–0.29 ms) plus the extra mode-sync signature
round trip B5 always performs — cryptographic cost, as expected.

At reduced availability, the mean jumps by roughly **two orders of
magnitude**, to a value close to `wait_timeout_seconds: 0.05` (50 ms) in
`config/pilot.yaml`. This is the bounded wait itself: a transaction that
lands in the controller's degraded band (`pool_min_wait ≤ fraction <
pool_min_hybrid`) waits up to 50 ms for the pool to recover before
falling back. The mean sits below 50 ms rather than at it because not
every non-hybrid transaction waits — one that finds the pool already
below `pool_min_wait` gets an immediate `PQC_ONLY` with no wait, and
emergency-flagged transactions (5% of the workload) skip the wait
unconditionally. The pooled mean is a mix of ~0 ms (no-wait fallback),
~50 ms (waited then fell back or recovered), and ~0.3 ms (immediate
hybrid) transactions.

`fallback_frequency` rises with device count at the same availability
level (0.5: 0.032→0.047; 0.0: 0.850→0.999) because more devices drain
the same-sized pool faster relative to its fixed regeneration rate — the
pool empties earlier in the run at higher load, so a larger share of the
window is spent in the degraded/unavailable bands.

**This did not appear in any measurement taken before commit `21f3099`.**
Before that fix, the wait was never executed, so B5's degraded-band
latency was indistinguishable from an immediate fallback (~0.3 ms). A
figure like "0.404 ms" cited earlier in this project's history — before
this pilot existed — cannot have come from a system exhibiting this
behavior, and should be treated as superseded by the numbers above, not
reconciled with them.

## 3. B3 and B4 collapse together under outage; B5 does not

The project's central behavioral claim, in the numbers:

| Baseline | qkd=0.0, devices=1000: successful_transmission_rate |
|---|---|
| B3 (QKD-only) | 0.002 (100/50,000) |
| B4 (static hybrid) | 0.002 (100/50,000) |
| B5 (adaptive hybrid) | 0.997 (49,842/50,000) |

B3 and B4 land on the same success rate to three decimal places — both
fail almost immediately once the pool's initial charge is spent, because
neither has a fallback path. B5, given the identical QKD-availability
condition, keeps succeeding via the PQC-only path. All three other
baselines (B1, B2, and B5 at qkd=1.0) sit at 0.99+ throughout, so the
~0.3% shortfall seen even in the "healthy" cells is attributable to
nominal-load packet loss (`packet_loss_probability` per hop in
`src/network/topology.py`), not key establishment.

## 4. What is not analyzed here

- No statistical test for whether any of the above differences are
  significant beyond what the bootstrap CIs show.
- No figures.
- No comparison across `payload_class` or `network_load` — the pilot
  held both constant (`medium`, `nominal`); the full study's matrix
  would vary them.
- `payload_encryption_ms_mean` is reported (added to the aggregator for
  this analysis) but not discussed above — it is small (~0.03–0.04 ms)
  and roughly constant across baselines and conditions, as expected
  for a fixed-size AES-256-GCM operation on a fixed payload class.
- No claim about `wait_timeout_seconds`'s value being well-chosen. The
  pilot's stated purpose (Task 7 Part 7) is exactly to inform that kind
  of decision for the full study, not to validate the pilot's own
  provisional defaults.
