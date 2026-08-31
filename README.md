# 6G-Quantum-EHR-Paper

**Latency-Aware Adaptive QKD-PQC Key Establishment for Electronic Health
Record Sharing in 6G-Edge Healthcare Networks**

**Authors:** Ramana Sree K V, Verona Ann Mariya

> ### Status: implementation validated — **pilot NOT run**
>
> This repository contains a validated simulation implementation and the
> research record behind it. **No experiment has been run and no results
> exist.** `results/` is empty. Nothing here should be read as an
> experimental finding. Running the pilot is the next stage --
> see `docs/research_plan.md`'s "Roadmap status" section for how this
> maps to the original 12-task framework.

---

> **Scope: this is a simulation study, not a hardware study.** Cryptographic
> operations are real (ML-KEM-768 and ML-DSA-65 via `liboqs`), but they are
> measured on the simulation host. The project makes **no claim** about PQC
> performance on constrained IoMT devices or embedded platforms. See
> `docs/scope_and_claims.md` before writing or citing any result.

## 1. What this project investigates

Quantum Key Distribution (QKD) offers strong key-establishment
guarantees but is a **finite, interruptible resource**: key material is
generated at a bounded rate into a bounded pool, and a channel outage
drains it. Post-Quantum Cryptography (PQC) is always available but rests
on computational assumptions.

The question this project asks is whether **adaptively** choosing
between a QKD+PQC hybrid and a PQC-only fallback — per session, based on
observed QKD availability — gives better latency and availability
characteristics for EHR sharing over 6G-edge healthcare networks than
the fixed alternatives, and what it costs in communication overhead.

The primary independent variable is **QKD availability**. The primary
measured outcomes are key establishment latency, end-to-end EHR
transaction latency, successful transmission rate, communication
overhead, and fallback frequency.

## 2. What is currently implemented

A discrete-event simulation (SimPy) in which every cryptographic
operation is **real, not mocked or approximated**:

- ML-KEM-768 and ML-DSA-65 via `liboqs` — real NIST-standardized
  implementations, with library-reported sizes measured at call time
  rather than hard-coded.
- AES-256-GCM and HKDF via `cryptography`.
- X25519 / Ed25519 for the classical baseline.
- QKD as a **simulated availability resource** (see §4).

All five baselines, the adaptive controller, the synthetic EHR workload,
the network abstraction, raw-first metrics collection, and a test suite
covering the critical behaviours. **60 tests pass** and
`experiments/validate_phase17.py` reports **8/8**, in the environment
recorded in `docs/environment_manifest.md`.

## 3. The five baselines

All five implement the same interface and share the same AEAD, framing,
and logging. They differ **only** in key establishment.

| ID | Baseline | Key establishment | Under QKD outage |
|---|---|---|---|
| **B1** | Classical | X25519 + Ed25519 | Unaffected (does not use QKD) |
| **B2** | PQC-only | ML-KEM-768 + ML-DSA-65 | Unaffected (does not use QKD) |
| **B3** | QKD-only | QKD pool draw (+ ML-DSA auth) | **Fails** — the unmitigated-outage reference point |
| **B4** | Static hybrid | QKD ‖ ML-KEM via HKDF, always both | **Fails** — does *not* fall back |
| **B5** | Adaptive hybrid | Controller selects hybrid or PQC-only per session | **Falls back to PQC-only and succeeds** |

**The B4/B5 divergence is the central behavioural claim of the project.**
B4 must never silently behave like B5. This is asserted directly by
`tests/test_integration_scenarios.py::test_b4_vs_b5_diverge_under_outage_the_critical_distinction`,
which runs both under an identical forced outage and requires B4 to fail
while B5 succeeds in PQC-only mode.

B3's "QKD-only" refers to the *session key material only* — its
classical control channel is still ML-DSA-authenticated, so the
baselines differ in key establishment rather than in authentication
strength.

## 4. The QKD model

**QKD is modeled as a simulated resource, not as quantum physics.** There
are no photons, no basis reconciliation, and no quantum-mechanical
simulation anywhere in this repository. No experimental QKD hardware
results are claimed.

`src/crypto/qkd.py` models a bounded key-material pool with: generation
at a configurable rate, bounded capacity, per-session consumption, an
availability fraction, depletion, outage injection (generation stops,
draws continue to drain), and recovery.

`draw()` **raises** when material is insufficient — it never falls back.
That decision belongs to the controller, and keeping it out of the QKD
module is what makes the B4/B5 distinction structurally enforceable.

QKD pool capacity, generation rate, and the availability→rate mapping
are **modeled assumptions and sensitivity variables**, not
literature-measured facts. See `docs/implementation_notes.md` Part II §5
for the full parameter-provenance table.

## 5. The hybrid construction

```
IKM         = QKD_secret || ML-KEM_shared_secret
PRK         = HKDF-Extract(salt, IKM)
session_key = HKDF-Expand(PRK, info, L)
```

Context is bound through HKDF's `info` parameter, not concatenated into
the IKM.

**This is an engineering-level key combination.** It is **not** a
formally proven QKD-PQC combiner, and no compositional security proof is
claimed for this instantiation. The claim wording is pinned in code as
`src.crypto.hybrid.SECURITY_CLAIM` so it cannot drift into an overclaim.
Do not strengthen this claim in the manuscript.

## 6. Repository structure

```
6G-Quantum-EHR-Paper/
├── src/
│   ├── crypto/        classical, pqc, qkd, hybrid, authentication, interfaces
│   ├── network/       topology, channel, edge
│   ├── workload/      ehr_generator  (synthetic only)
│   ├── adaptive/      controller
│   ├── baselines/     baselines      (B1-B5)
│   ├── simulation/    simulator, events
│   ├── metrics/       collector (raw), aggregator
│   └── utils/         config, random (seeding), logging
├── tests/             7 test modules, 50 tests
├── experiments/       run_pilot.py, validate_phase17.py
├── config/            pilot.yaml, full_experiment.yaml (inert placeholder)
├── results/           raw/  processed/  figures/     <- EMPTY, pilot not run
├── docs/
│   ├── implementation_notes.md   implementation reference + Task 8 record
│   ├── research_plan.md
│   ├── notes.md
│   └── task_logs/     Tasks 1-8 research record
├── research/          literature_matrix.csv, research_gaps.md
├── paper/             manuscript/, references/, figures/, tables/
├── requirements.txt
└── pyproject.toml
```

## 7. Setup and testing

Dependencies are listed in `requirements.txt`. **`liboqs` (the C
library) is not installed via pip** — it requires a separate build.
The exact build steps used for Task 8 (a minimal build enabling only
ML-KEM-768 and ML-DSA-65) are in `docs/implementation_notes.md` Part II §1.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt   # exact validated versions
# then build liboqs at the commit pinned in docs/environment_manifest.md
```

**Python 3.12 is required** — `requirements.txt` pins `numpy>=2.5`, which
needs Python >= 3.12, so the dependency set is unresolvable on 3.11.
`docs/environment_manifest.md` records the full validated stack, including
the exact liboqs commit.

Run the test suite:

```bash
pytest tests/ -v
```

Re-run the eight Task 8 validation checks end-to-end:

```bash
python experiments/validate_phase17.py
```

## 8. Running the simulation

> The pilot has **not** been run. These commands are documented so the
> next stage is reproducible — not as a record of anything executed.

One pilot cell:

```bash
python experiments/run_pilot.py \
    --config config/pilot.yaml \
    --seed 42 \
    --output results/raw/pilot \
    --baseline B5 \
    --qkd-availability 0.5 \
    --device-count 10
```

The full 30-configuration pilot requires an explicit `--full-pilot`; it
is deliberately not the default.

Raw per-transaction events are written as JSON-lines to
`results/raw/`, alongside an `environment.json` recording config path,
seed, Python version, platform, and timestamp. Metrics are always
derived from those raw rows, never from pre-aggregated values.
Aggregates belong in `results/processed/`.

Figures are **not** generated yet. No figure pipeline exists — it will
be built once real results exist to plot.

## 9. Reproducibility

One top-level seed drives everything; `SeedManager` derives a stable,
named sub-seed per stochastic component so components cannot perturb one
another's sequences. Every run records its own provenance. Experiment
identifiers encode the full cell definition.

`docs/implementation_notes.md` Part II §4.2 documents a real
reproducibility bug found and fixed during Task 8 validation, and the
lesson generalized from it: *a reproducibility claim tested only under
conditions where the randomness rarely fires is not a confirmed claim.*

## 10. What has NOT been done

- The pilot experiment has not been run. `results/` is empty.
- No figures, tables, or Results-section content exist.
- Between-baseline hypothesis testing is not implemented.
- The full-study matrix is not committed to; `config/full_experiment.yaml`
  is an inert placeholder marked `status: NOT_READY`.
- Open items found during the Git import are recorded in
  `docs/implementation_notes.md` Part III and need author review before
  the pilot runs.

**Next stage: run the pilot.** (Not "Task 9" -- that number already
belongs to the evaluation-methodology task, completed earlier. See
`docs/research_plan.md`'s "Roadmap status" section.)

## 11. Documentation

| Document | Contents |
|---|---|
| `docs/implementation_notes.md` | Implementation reference, liboqs build steps, measured PQC parameters, parameter provenance, known limitations, import-review findings |
| `docs/environment_manifest.md` | Exact validated environment: Python, dependency and liboqs versions, build flags, validation status |
| `docs/scope_and_claims.md` | **What this project does and does not claim.** Simulation-only scope boundary; rules for reporting results |
| `docs/task_logs/` | The Tasks 1–8 research record, including the Task 8 completion report |
| `docs/research_plan.md` | Phased research plan |
| `research/literature_matrix.csv` | Structured literature tracking with verification status |
| `paper/references/references_verified_only.bib` | Only entries with independently confirmed DOIs |

## License

MIT — see `LICENSE`.
