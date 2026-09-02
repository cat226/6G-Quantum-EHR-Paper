# Implementation Notes

**Project:** Latency-Aware Adaptive QKD-PQC Key Establishment for
Electronic Health Record Sharing in 6G-Edge Healthcare Networks
**Authors:** Ramana Sree K V, Verona Ann Mariya
**Status:** Task 8 implementation, validated. **The pilot experiment has
NOT been run.** No experimental results exist in this repository.

This document has two parts:

- **Part I — Implementation reference.** What each component is and
  where it lives. Written when the Task 8 implementation was imported
  into this Git repository.
- **Part II — Implementation record (authored during Task 8).** The
  original Task 8 notes, preserved. Build steps, measured PQC
  parameters, the two bugs found during validation, the parameter
  provenance table, and known limitations.

---

# PART I — IMPLEMENTATION REFERENCE

## I.1 Project purpose

The project investigates whether **adaptively** switching between a
QKD+PQC hybrid key establishment and a PQC-only fallback gives better
latency and availability characteristics for EHR sharing over 6G-edge
healthcare networks than the fixed alternatives — and at what cost in
communication overhead.

The comparison is made by discrete-event simulation across five key
establishment strategies (B1–B5, Section I.6). The independent variable
of primary interest is **QKD availability**; the primary dependent
variables are key establishment latency, end-to-end EHR transaction
latency, successful transmission rate, and fallback frequency.

## I.2 Scope of the Task 8 implementation

In scope, implemented, and tested:

- Real cryptography for every primitive (Section I.3) — nothing mocked.
- QKD as a **simulated resource pool** (Section I.4) — not quantum physics.
- The HKDF hybrid construction (Section I.5).
- All five baselines (Section I.6) with a preserved B4/B5 distinction.
- The adaptive controller (Section I.7).
- Synthetic EHR workload generation (Section I.8).
- A simplified 6G-edge network abstraction (Section I.9).
- Raw-first metrics collection and aggregation (Section I.10).
- Seeded reproducibility (Section I.11) and a test suite (Section I.12).

Explicitly **out** of scope: quantum-physical simulation, a full 6G
protocol stack, real patient data, formal security proofs, embedded /
constrained-device performance claims, and any experimental result.

**This is a simulation study, not a hardware study.** Cryptographic timings
are measured on the simulation host; there is no device-class model. See
`docs/scope_and_claims.md` for the full claims boundary and the rules for
reporting results — it governs what the manuscript may assert.

## I.3 Cryptographic primitives

| Role | Algorithm | Module | Library |
|---|---|---|---|
| PQC key encapsulation | **ML-KEM-768** | `src/crypto/pqc.py` | `liboqs` via `oqs` |
| PQC signature | **ML-DSA-65** | `src/crypto/pqc.py` | `liboqs` via `oqs` |
| AEAD (all baselines) | **AES-256-GCM** | `src/crypto/classical.py` | `cryptography` |
| Key derivation / combiner | **HKDF** (SHA-256) | `src/crypto/hybrid.py` | `cryptography` |
| Classical KEX (B1 only) | X25519 | `src/crypto/classical.py` | `cryptography` |
| Classical signature (B1 only) | Ed25519 | `src/crypto/classical.py` | `cryptography` |

Algorithm names are asserted in `tests/test_pqc.py` so that a silent
substitution would fail the test suite. `src/crypto/interfaces.py`
defines the shared shapes every baseline implements — a structural
fairness mechanism, so baselines can differ only in key establishment,
never in AEAD or framing.

AES-256-GCM is shared by **all** baselines by design. Only key
establishment differs between them.

## I.4 QKD abstraction

`src/crypto/qkd.py`. QKD is modeled as a **bounded key-material pool**,
not as a quantum-mechanical process. No photons, no basis
reconciliation, no QBER-driven distillation.

The model provides: key generation (`tick()` accrues material at a
configurable rate), a bounded pool (`capacity_bits`), consumption
(`draw()`), availability (`available_fraction()`), depletion (`draw()`
raises `QKDInsufficientMaterial`), outage injection (`set_outage(True)`
suspends generation while draws continue to drain the pool), and
recovery (`set_outage(False)`).

**`draw()` never falls back.** It raises. Deciding what to do about an
empty pool belongs to the baseline or the adaptive controller, and is
kept out of this module deliberately — that separation is what keeps B4
and B5 behaviourally distinct.

The bytes returned by `draw()` are `os.urandom` output standing in for
"unpredictable key material of the requested length". This is a
modeling stand-in for *availability*, and is **not** a claim to QKD's
information-theoretic security property.

## I.5 Hybrid construction

`src/crypto/hybrid.py`. The approved construction, unchanged:

```
IKM         = QKD_secret || ML-KEM_shared_secret
PRK         = HKDF-Extract(salt, IKM)
session_key = HKDF-Expand(PRK, info, L)
```

with `info` = the per-session context label, and `L` = 32 bytes.
Context is bound through HKDF's `info` parameter, **not** concatenated
into the IKM — that was Task 7.1's correction to the original draft.
`salt=None` (RFC 5869 treats an absent salt as zeros); no independent
salt source is modeled.

**Security claim.** This is an **engineering-level key combination**
using HKDF over independently generated QKD and ML-KEM secrets. It is
**not** a formally proven QKD-PQC combiner, and no compositional
security proof is claimed for this instantiation. The exact claim
wording is pinned in code as `hybrid.SECURITY_CLAIM` so it cannot drift
into an overclaim elsewhere. Do not strengthen this claim in the
manuscript.

## I.6 Baseline definitions

`src/baselines/baselines.py`. All five expose the same
`establish_session_key(context) -> SessionResult` interface.

| ID | Name | Key establishment | Behaviour when QKD is unavailable |
|---|---|---|---|
| **B1** | Classical | X25519 (+ Ed25519 auth) | Unaffected — does not use QKD |
| **B2** | PQC-only | ML-KEM-768 (+ ML-DSA-65 auth) | Unaffected — does not use QKD |
| **B3** | QKD-only | QKD pool draw (+ ML-DSA-65 auth) | **Fails.** No fallback — this is the unmitigated-outage comparison point |
| **B4** | Static hybrid | QKD ‖ ML-KEM via HKDF, **always both** | **Fails.** Does *not* fall back to PQC |
| **B5** | Adaptive hybrid | Controller picks hybrid or PQC-only per session | **Falls back to PQC-only** and succeeds |

**The B4/B5 distinction is the single most important behavioural
property in the project.** B4 catches `QKDInsufficientMaterial` and
returns a *failed* `SessionResult`; it has no path to a PQC-only key.
B5 consults the controller first and takes the PQC-only path when told
to. The contrast is asserted directly in
`tests/test_integration_scenarios.py::test_b4_vs_b5_diverge_under_outage_the_critical_distinction`,
which runs both under an identical forced outage and requires B4 to
fail and B5 to succeed in `PQC_ONLY` mode.

"QKD-only" (B3) refers to the **session-key material only**. B3's
classical control channel is still authenticated with ML-DSA-65 — the
same mechanism as the proposed system — so the baselines differ in key
establishment rather than in authentication strength.

Every `EstablishedKey` records a `KeySource` (`classical`, `pqc_only`,
`qkd_only`, `static_hybrid`, `adaptive_hybrid`). Which mode was
*actually* used is therefore recoverable from the raw logs, rather than
inferred from what the config intended — this is the check for whether
the system genuinely behaves adaptively or merely looks adaptive.

## I.7 Adaptive controller

`src/adaptive/controller.py`. Reads the QKD pool's fill fraction and
returns a `ControllerDecision`. It **never touches key material** — its
entire public surface is one method, `select_mode()`, and a test
asserts exactly that.

States: `QKD_AVAILABLE`, `QKD_DEGRADED`, `QKD_UNAVAILABLE`, and
`PQC_FALLBACK` (a *decision* state, as distinct from the *pool* state
`QKD_UNAVAILABLE`).

Decision logic, in order:

1. `fraction >= pool_min_hybrid` → **HYBRID** (`QKD_AVAILABLE`).
2. Criticality is `EMERGENCY` → **PQC_ONLY** immediately
   (`PQC_FALLBACK`). Emergency transactions never wait.
3. `fraction >= pool_min_wait` → bounded wait of
   `wait_timeout_seconds`, then re-check: recovered → **HYBRID**,
   otherwise **PQC_ONLY** (`PQC_FALLBACK`).
4. Otherwise → **PQC_ONLY** (`QKD_UNAVAILABLE`).

Clinical criticality is only a *wait-skip* input, not a primary
decision axis, and is not swept as an independent variable in the pilot.

The bounded wait takes an injected `wait_fn(seconds)` so the controller
stays decoupled from the simulation engine. `B5Adaptive` injects the QKD
pool's own `tick()` as that function, so the wait advances simulated time
and the pool may replenish across the threshold. Because `tick()` is a
no-op during an outage, waiting through an outage correctly yields no
replenishment. See Part III finding F1 (resolved in Task 8.5).

## I.8 EHR workload

`src/workload/ehr_generator.py`. **Synthetic only. No real patient data
exists anywhere in this repository.** Bodies are FHIR-*inspired* nested
dicts padded with a clearly-labeled `_synthetic_filler` field — a
controllable, repeatable payload size, not a claim of FHIR conformance.
`tests/test_workload_network_metrics.py::test_no_real_patient_data_markers`
asserts the absence of real-record-shaped fields.

Configurable: payload class and size ranges (small 1–5 KB, medium
20–80 KB, large 200 KB–1 MB), transaction type (read/write/share),
emergency fraction (default 0.05), device count and transactions per
device (via the experiment config), and the seed. Deterministic under a
given seed via a private `random.Random` instance.

## I.9 Network model

`src/network/topology.py` (+ `channel.py`, `edge.py`). A deliberately
simplified abstraction of the chain:

```
EHR client / IoMT → 6G access abstraction → edge gateway
                  → hospital network → EHR server
```

modeled as three `NetworkLink` hops. **This is not a 6G protocol stack.**
There is no PHY, no MAC, no radio protocol, and nothing here reproduces
a finalized 6G standard — 6G standards are not finalized.

Configurable per `NetworkParameters` profile (`nominal`, `congested`):
propagation delay, processing delay, transmission rate, packet loss
probability, and edge processing delay. Per-hop latency is
propagation + processing + (payload_bits / rate). Loss is a per-attempt
probability; a single dropped hop fails the transaction, and no
retransmission or queueing is modeled.

Edge processing (`edge.py`) contributes only the small non-crypto
adaptive-decision overhead. Real cryptographic cost is *measured* by
actually calling the crypto modules, never modeled as a constant.

## I.10 Metrics

`src/metrics/collector.py` writes one `TransactionEvent` per
transaction as **JSON-lines, raw, before any aggregation**. Each row
carries its full identifying context (timestamp, experiment id,
baseline, configured QKD availability, device count, payload class,
network load, seed), so raw logs are self-describing and never depend
on filename parsing.

Captured per transaction: success, key establishment latency,
**payload encryption latency**, network latency, end-to-end latency,
communication overhead (bytes), payload bytes, the `KeySource` actually
used, the controller state, and the failure reason. Cryptographic
per-operation timings (keygen, encap, decap, sign, verify) are captured
in the key metadata.

**AES-256-GCM is exercised once per successful transaction.** Every
baseline shares one `AESGCMEncryption` instance (structural fairness,
Section I.6), and the simulator now actually calls it: the EHR payload is
encrypted and decrypted (round trip) with the derived session key before
transmission, and the network layer transmits the resulting ciphertext
size (payload + 12-byte nonce + 16-byte GCM tag), not the raw plaintext
size. The round-trip cost is recorded as `payload_encryption_ms` and is
included in `end_to_end_ms`. A failed transaction never reaches
encryption and records `payload_encryption_ms=0.0`, never a fabricated
cost.

`src/metrics/aggregator.py` derives per-cell summaries from those raw
rows: mean / median / p95, bootstrap 95% CI (no normality assumption,
because the controller's bounded wait is expected to right-skew the
latency distribution), successful transmission rate, mean communication
overhead, and **fallback frequency** (the fraction of B5 sessions that
took the PQC-only path).

Not implemented: between-baseline hypothesis testing, throughput as a
distinct aggregate, and CPU/memory sampling. See Part II Section 6 and
Part III.

## I.11 Reproducibility design

- **Seeds.** One top-level seed; `src/utils/random.py`'s `SeedManager`
  derives a stable, named sub-seed per component so adding a workload
  draw cannot perturb the network's random sequence.
- **Config files.** `config/pilot.yaml` holds the pilot matrix,
  thresholds, pool sizing, and base seed. `config/full_experiment.yaml`
  is an inert placeholder marked `status: NOT_READY`.
- **Provenance capture.** Every run writes `environment.json` next to
  the raw results: config path, seed, Python version, platform,
  timestamp, and liboqs-python version.
- **Experiment identifiers.** Each cell gets a descriptive
  `experiment_id` encoding baseline, QKD availability, device count,
  payload class, network load, and seed; it names the output file.
- **Raw storage.** `results/raw/` (JSON-lines), aggregates in
  `results/processed/`. Both empty — the pilot has not been run.

Reproducibility was verified during Task 8 under conditions where the
randomness actually fires — see Part II Section 4.2, which is worth
reading before making any future reproducibility claim.

## I.12 Testing status

**60 tests pass** in the validated environment (Task 8.5): the original
50 from Task 8, plus 10 added in Task 8.5 covering the adaptive
bounded-wait path. `tests/` covers:

| Area | File |
|---|---|
| QKD pool depletion, outage, recovery, no-fallback | `test_qkd_pool.py` |
| HKDF combiner: determinism, input sensitivity, context separation, length | `test_hybrid_kdf.py` |
| ML-KEM-768 / ML-DSA-65 round trips, tamper rejection, library-reported sizes | `test_pqc.py` |
| Modular authentication (Ed25519 and ML-DSA) | `test_authentication.py` |
| Adaptive switching, thresholds, emergency wait-skip, primitive isolation | `test_adaptive_controller.py` |
| **B4/B5 divergence**, PQC fallback, QKD-only failure | `test_integration_scenarios.py` |
| EHR generation, network delay, metric calculation | `test_workload_network_metrics.py` |
| **Adaptive bounded wait**: recovery, non-recovery, zero-timeout, B4 divergence, simulated-vs-wall-clock time, determinism | `test_b5_wait_path.py` |

`experiments/validate_phase17.py` re-runs the eight Task 8 validation
checks end-to-end; all 8 pass in the validated environment.

Environment: see `docs/environment_manifest.md` for the exact Python,
dependency, and liboqs versions this was validated against.

## I.13 Repository layout note

The Task 8 implementation previously lived in an `implementation/`
subdirectory of a larger workspace. On import it was **flattened to the
repository root** (`src/`, `tests/`, `experiments/`, `config/`,
`results/`, `requirements.txt`, `pyproject.toml`), so that `pytest` and
the `src.*` import paths work from the repository root. No file
contents were changed.

Two docstrings in `src/adaptive/controller.py` and `src/crypto/qkd.py`
still refer to `implementation/config/pilot.yaml`. The current path is
`config/pilot.yaml`. Source files were deliberately left untouched
during import; this is recorded here rather than silently edited.

---

# PART II — IMPLEMENTATION RECORD (authored during Task 8)

_Preserved as written during Task 8. Section numbers below are the
original ones._


---

## 1. liboqs build process (exact steps used in this environment)

Task 8 Phase 1 required documenting the issue if liboqs/Python bindings
are unavailable or problematic, rather than silently substituting a
different algorithm. That situation was encountered and resolved, not
avoided:

1. `pip install liboqs-python` succeeds (installs the Python wrapper),
   but the wrapper's automatic liboqs (C library) auto-build failed on
   first attempt: `cmake: not found`.
2. Installed build prerequisites via apt: `cmake`, `ninja-build`,
   `build-essential` (already present), `libssl-dev`.
3. The wrapper's *default* auto-build attempts to build **every**
   algorithm in liboqs, which is unnecessarily slow for this project
   (only ML-KEM-768 and ML-DSA-65 are needed). Instead of relying on the
   wrapper's auto-build, liboqs was built manually with a minimal
   algorithm set:
   ```
   git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
   cd liboqs && mkdir build && cd build
   cmake -GNinja -DCMAKE_BUILD_TYPE=Release \
     -DOQS_MINIMAL_BUILD="KEM_ml_kem_768;SIG_ml_dsa_65" \
     -DOQS_BUILD_ONLY_LIB=ON -DBUILD_SHARED_LIBS=ON ..
   ninja
   ```
4. The resulting `liboqs.so` was installed system-wide:
   ```
   cp build/lib/liboqs.so* /usr/local/lib/
   ldconfig
   ```
5. Verified via the real `oqs` Python API (not just that the library
   loads) -- see Section 3's measured values below.

**No algorithm substitution occurred.** ML-KEM-768 and ML-DSA-65, the
exact NIST-standardized algorithms specified throughout Tasks 6-8, are
what's actually running.

---

## 2. Structural deviations from Task 8 Phase 2's requested layout

Two files were kept as thin re-exports rather than independent
implementations, to avoid duplicating logic across files that would
otherwise need to stay in lockstep:

- `src/network/channel.py` re-exports `NetworkLink`/`NetworkParameters`
  from `topology.py`. A "channel" and the topology it's used within are
  not meaningfully separable in this design (Task 8's own Phase 10
  describes the topology and its link characteristics together).
- `src/simulation/events.py` re-exports `TransactionEvent` from
  `src/metrics/collector.py`. The dataclass and the collector that
  writes it are tightly coupled (the collector's `record()` method is
  typed directly against it); splitting them would add an import hop
  with no benefit.

Both are explained here per Task 8's instruction ("explain the change
before making it") rather than silently deviating from the requested
structure. Every other file in Task 8 Phase 2's layout exists as
specified, with real logic.

---

## 3. PQC parameters -- measured, not recalled (supersedes Task 7/7.1)

Tasks 7 and 7.1 explicitly labeled these values `RECALLED-UNVERIFIED`
and refused to state them as fact without verification. They are now
**measured directly from the real, running liboqs build** via
`kem.details` / `sig.details`:

| Algorithm | Field | Value | How obtained |
|---|---|---|---|
| ML-KEM-768 | public key | 1184 bytes | `oqs.KeyEncapsulation('ML-KEM-768').details['length_public_key']` |
| ML-KEM-768 | ciphertext | 1088 bytes | `...['length_ciphertext']` |
| ML-KEM-768 | shared secret | 32 bytes | `...['length_shared_secret']` |
| ML-KEM-768 | secret key | 2400 bytes | `...['length_secret_key']` |
| ML-DSA-65 | public key | 1952 bytes | `oqs.Signature('ML-DSA-65').details['length_public_key']` |
| ML-DSA-65 | signature | 3309 bytes | `...['length_signature']` |
| ML-DSA-65 | secret key | 4032 bytes | `...['length_secret_key']` |

Observed single-operation timings from this environment (illustrative
of the *order of magnitude* only -- these are NOT the pilot's actual
results, and will vary run to run and by hardware; the pilot's real,
aggregated timings belong in `results/`, not here):
ML-KEM-768 keygen ~1.7 ms / encap ~0.1 ms / decap ~0.02 ms;
ML-DSA-65 keygen ~0.1 ms / sign ~0.1 ms / verify ~0.04 ms.

Interesting, worth noting plainly: these measured byte sizes match what
Task 7 recalled from training-data memory almost exactly. That is a
reassuring cross-check, not a substitute for having actually measured
them -- the point of Task 7.1's "do not use recalled values" instruction
was exactly this: don't rely on the recollection being right by luck.
Now it doesn't need to be trusted at all; it's measured.

---

## 4. Two real bugs found and fixed during validation

Documented explicitly rather than silently patched, per this project's
standing practice of surfacing findings rather than hiding them.

### 4.1 QKD pool calibration (found during Phase 17 validation)

**Symptom**: at `qkd_availability_config=0.5` with 20 simulated devices
over a 5-second window, every single transaction landed in
`MODE_HYBRID` -- the availability parameter had no visible effect. The
pool (originally sized as a large, fixed 8,000,000-bit constant with a
generation rate scaled only to that same constant) never drained
meaningfully relative to a 256-bit-per-session draw.

**Fix**: pool capacity is now sized relative to a session's draw
(`sessions_buffer x QKD_BITS_PER_SESSION`, default `sessions_buffer=20`
-> capacity = 5,120 bits), and the full-availability generation rate is
anchored to "regenerate the whole pool in ~1 simulated second" instead
of ~2. Re-validated: at 20 devices / 200 transactions over ~1 simulated
second of elapsed pool time, availability=1.0 -> 200/200 hybrid;
availability=0.5 -> 114/200 hybrid, 86/200 fallback; availability=0.0 ->
15/200 hybrid (initial pool charge draining), 185/200 fallback. The
parameter now has real, monotonic, visible effect.

**Still flagged as unresolved**: `sessions_buffer=20` and the "~1
second" anchor are themselves MODELED ASSUMPTIONS, not literature
figures -- they were chosen to make the pilot *informative*, not to
match any specific real QKD system's buffering behavior. Task 6 Section
19.3 already flagged "QKD pool-model realism" as an implementation risk
worth a sanity check against real dynamics; this remains open and
should be revisited once the outstanding literature fetches (Task 7
Part 1/3) are resolved.

### 4.2 Network-layer reproducibility (found during Phase 17 validation)

**Symptom**: `Topology.build()` was called without a seeded RNG in
`simulator.py`, so packet-loss decisions used an unseeded
`random.Random()` internally. A same-seed reproducibility check
initially reported "confirmed" -- but only because the nominal packet
loss probability (0.1%) was low enough that no loss occurred in either
run by chance. This was not a real confirmation.

**Fix**: `Topology.build()` is now called with `random.Random(config.seed
+ 1)`, tying network-layer randomness to the experiment seed. Re-verified
using `network_load="congested"` (2% loss) and `PayloadClass.LARGE`
specifically to force real loss events: two independent runs with the
same seed produced 4/100 failures each, in the same positions, with 0
mismatches across all deterministic fields. This is a genuine
confirmation, not a lucky one.

**Lesson generalized**: any reproducibility claim tested only under
conditions where the tested randomness rarely fires is not actually a
confirmed claim. This is noted here so it isn't repeated when the full
pilot's reproducibility is checked at other parameter combinations.

---

## 5. Parameter provenance (extends Task 7 Part 10's canonical table)

| Parameter | Value | Type | Notes |
|---|---|---|---|
| ML-KEM-768 / ML-DSA-65 sizes | See Section 3 | **MEASURED** (real liboqs) | Supersedes Task 7's RECALLED-UNVERIFIED figures |
| QKD bits drawn per session | 256 | Internally derived | Matches AES-256 key length |
| QKD pool capacity | `sessions_buffer x 256` (default 5,120 bits) | MODELED ASSUMPTION | Section 4.1's fix; sensitivity-testable |
| QKD generation rate mapping | Linear in availability, full-rate = capacity/1.0 sec | MODELED ASSUMPTION | Section 4.1; explicitly a SENSITIVITY VARIABLE |
| Adaptive thresholds (pool_min_hybrid, pool_min_wait, wait_timeout) | 0.3, 0.1, 0.05s (pilot default) | MODELED ASSUMPTION | `config/pilot.yaml`; not literature-sourced |
| EHR payload size ranges | Small 1-5KB, Medium 20-80KB, Large 200KB-1MB | MODELED ASSUMPTION | Unchanged from Task 7 Part 4 |
| Network latency/throughput/loss (nominal, congested) | See `src/network/topology.py` `NetworkParameters` | MODELED ASSUMPTION | Unchanged in kind from Task 7 Part 5; concrete values now exist in code where Task 7 only bracketed ranges |

---

## 6. Known limitations (carried forward, not resolved by implementation)

- The hybrid combiner's security claim remains Task 7.1's Claim C
  (engineering-level combination, no compositional proof) -- writing
  working code for it does not change that claim; Section 1's
  outstanding citation verification is still needed before manuscript
  writing.
- QKD pool/rate parameters remain MODELED ASSUMPTIONS/SENSITIVITY
  VARIABLES, not literature-measured facts, per Section 4.1 above.
- EHR payload and network parameters remain MODELED ASSUMPTIONS per
  Task 7 Parts 4-5, now instantiated as concrete default values in code
  rather than ranges in prose -- this is a narrowing of the earlier
  ranges for implementation purposes, not new evidence justifying the
  specific numbers chosen.
- The multi-site topology extension (Task 6 Section 9's "optional")
  is not implemented -- `networkx` is a listed dependency but currently
  unused, kept only because a future multi-site extension might need
  it.
- Statistical test selection (Task 7 Part 8: Mann-Whitney U as the
  default, with a normality-check escape hatch to a t-test) is not yet
  implemented as code -- `src/metrics/aggregator.py` currently computes
  descriptive statistics (mean/median/p95/bootstrap CI) but not
  between-baseline hypothesis tests. This is deferred to when real
  pilot data exists to test against, consistent with Task 8 Phase 18's
  "do not generate final paper results" instruction.

---

# PART III — OBSERVATIONS FROM THE GIT IMPORT REVIEW

These were noted while reading the implementation during its import
into this repository. **Nothing here has been fixed or changed** — the
Task 8 implementation was imported exactly as approved. These are
recorded so they are not lost, and they need author confirmation before
the pilot is run.

## F1 — The adaptive controller's bounded wait is inert in the pilot harness

> **STATUS: RESOLVED in Task 8.5** (commit "Fix adaptive QKD wait-path
> simulation"). `B5Adaptive` now injects `pool.tick` as the `wait_fn`, and
> the harness advances SimPy by `SessionResult.wait_seconds` so the pool
> clock, the simulation clock, and the recorded latency agree. Regression
> tests: `tests/test_b5_wait_path.py`. The diagnosis below is retained as
> the record of what was wrong.

`AdaptiveController.select_mode()` performs its bounded wait only when
an explicit `wait_fn` is injected. `B5Adaptive.establish_session_key()`
(`src/baselines/baselines.py`) calls it as
`self._controller.select_mode(pool, criticality)` — with no `wait_fn`.

Consequence, as the code currently stands: for a routine transaction in
the degraded band (`pool_min_wait <= fraction < pool_min_hybrid`), no
simulated time passes, the pool does not replenish, the post-wait
re-check sees the same fraction, and the decision is always
`PQC_ONLY`/`PQC_FALLBACK` — while still being recorded as
`waited=True` with `wait_seconds=wait_timeout_seconds`. The bounded-wait
recovery path therefore cannot succeed during a pilot run, and the
waiting time is not reflected in measured latency.

The controller's own unit tests do inject a `wait_fn` and do exercise
the recovery path, so the *controller* is correct and tested. The gap is
in the harness wiring, which no test currently covers.

This matters for interpretation: `wait_timeout_seconds` in
`config/pilot.yaml` has no effect on results as wired, and B5's
degraded-band behaviour is currently "immediate fallback" rather than
"try waiting, then fall back". **Confirm the intended behaviour before
running the pilot**, since it affects both the fallback-frequency metric
and B5's latency distribution.

## F2 — `mode_used` is serialized via `str()` on a `(str, Enum)` member

`src/simulation/simulator.py` records `mode_used = str(result.key.source)`,
which yields `"KeySource.PQC_ONLY"`. `src/metrics/aggregator.py` matches
that exact string, and the tests use the same form, so the pipeline is
**self-consistent as written**.

It is, however, dependent on CPython's `Enum.__str__` behaviour for a
`class KeySource(str, Enum)`. That representation has changed across
Python versions and would change again if `KeySource` were ever migrated
to `enum.StrEnum`, at which point `str()` would return `"pqc_only"` and
`fallback_frequency` would silently compute as `0.0` rather than error.
Worth pinning deliberately (either `.value` on both sides, or a test
asserting the serialized form) before results depend on it.

## F3 — Dead code in `run_cell()`

`src/simulation/simulator.py` retains `pool_capacity_bits = 8_000_000`
(explicitly commented as superseded by the Section 4.1 recalibration)
and an unused `QKDPoolConfig` import. Cosmetic only; the value is not
read. Flagged so it is not mistaken later for a live parameter that
contradicts the documented pool sizing.

## F4 — Raw-results storage policy is undecided

`results/raw/` is tracked, not ignored, so raw JSON-lines events are
preserved as research artifacts. At the pilot's largest cell
(1000 devices x 10 transactions x 5 repetitions) this will produce
substantial files. A decision is needed before the full pilot on
whether raw events stay in Git, move to Git LFS, or are archived
externally with only aggregates committed.

## F5 — `requirements.txt` is unpinned

> **STATUS: ADDRESSED in Task 8.5.** `requirements.lock.txt` now pins the
> full resolved dependency set, and `docs/environment_manifest.md` records
> the liboqs commit (`8979276ad1eb008215aa78a3c56b3649f604bbb1`), library
> version, build flags, and platform. `requirements.txt` is left unchanged
> as the Task 8 dependency specification. The per-run `environment.json`
> still captures only Python version, platform, and liboqs-python version —
> widening it to embed the full resolved set at run time remains open.


Dependencies are specified as lower bounds (`simpy>=4.1`,
`cryptography>=44.0`, ...), not pinned versions, and there is no
lockfile. `liboqs` itself is built from a `--depth 1` clone of `main`
with no recorded commit hash (Part II Section 1). For a reproducibility
claim in the manuscript, the exact resolved versions and the liboqs
commit should be captured at pilot time — `environment.json` currently
records the Python version, platform, and liboqs-python version, but not
the full dependency set or the liboqs C-library commit.

## F6 — Raw metrics output is append-mode, so re-runs silently accumulate

> **STATUS: RESOLVED** (commit "Fix M5: truncate metrics output per run,
> M3: exercise AES-256-GCM per transaction"). `MetricsCollector` now opens
> its output file with `"w"` instead of `"a"`. Within one run every
> `record()` call still accumulates in the same open file handle -- nothing
> within a run is lost -- but a rerun into the same path now overwrites
> cleanly instead of silently doubling. Verified: two full `run_cell()`
> invocations into an identical output path produce 36/36 transactions
> both times with zero deterministic-field mismatches, not 72. The
> diagnosis below is retained as the record of what was wrong.

Found during Task 8.5 validation. `MetricsCollector` opens its output
file with mode `"a"` (`src/metrics/collector.py`), which is deliberate —
the docstring explains it is append-friendly so a run need not be held in
memory. The consequence is that **re-running the same experiment id into
the same output directory appends to the previous run's file rather than
replacing it.**

Observed concretely: `experiments/validate_phase17.py` writes to a fixed
`/tmp/phase17_validation` path. Running it twice made check 4 ("single
end-to-end EHR transaction") fail with *"expected exactly 1 transaction,
got 2"* — the second run's event was appended to the first run's file.
Clearing the directory restored 8/8. Nothing was wrong with the
implementation; the validation script is simply not idempotent.

**This matters for the pilot run, more than it did here.** `run_pilot.py` uses
the same collector and derives its output filename from the experiment
id, which is deterministic for a given cell. Re-running a pilot cell —
after an interruption, a crash, or a parameter tweak — into an existing
`results/raw/` directory would silently double-count that cell's
transactions. Aggregates computed from it would be wrong in a way that
does not announce itself: no error, no warning, just inflated
`n_transactions` and a distorted distribution.

Not fixed here, because the append semantics are intentional and
changing them is a design decision rather than a defect repair. Before
the pilot runs, pick one:

- write each run into a fresh output directory (simplest, no code change);
- have the runner refuse to start when the target `.jsonl` already exists;
- or make the collector truncate, accepting the loss of append-resume.

Whichever is chosen, the pilot's raw output should be checked for
duplicate `transaction_id` values before any aggregation.
