# Paper Rewrite Audit — Phase 1

**Date:** 2026-09-01
**Branch:** `claude/pensive-bohr-1rdrrp`
**Commit at time of audit:** `95afe94` ("Add compiled manuscript PDF (30 pages)")
**Auditor note:** This document records facts gathered directly from the repository
(git log, source code, test runs, raw data files) as of the commit above. Nothing in
this file is inferred from the manuscript's own prose without independent verification
against the underlying artifact. Where a claim could not be independently verified in
this pass, it is marked explicitly rather than assumed true.

---

## 1. Current Manuscript Structure

`paper/manuscript/main.tex`, IEEEtran journal class, two-column, compiles cleanly to
**30 pages** (verified via `pdflatex`/`bibtex` full cycle; log confirms
`Output written on main.pdf (30 pages`, zero `!` errors, zero undefined
references/citations at last compile).

Section structure: Abstract/Keywords → Introduction (Motivating Scenario,
Contributions C1–C3, Scope) → Background (HNDL, PQC, QKD, 6G-Edge, Glossary,
Notation) → Related Work (Literature Verification Note, per-source discussion,
Broader Literature Landscape table, Detailed Comparison table, Research Gap table)
→ Threat Model (Adversary Model, In Scope T1–T6, Explicitly Not Defended Against)
→ System Architecture (Components, Component Placement Rationale, Trust
Boundaries, Data Flow) → Adaptive Mechanism (Algorithm 1, Worked Example,
Switching Granularity, Design Principles) → Cryptographic Design (primitives
table, Algorithm Selection Rationale, Alternative Constructions Considered,
Hybrid Key Derivation, Explicit Security Claim Boundary, Correctness Safeguard,
Novelty Guardrails) → Baselines (Why Five Baselines, Per-Baseline Protocol
Detail) → Simulation Implementation (environment table, Implementation
Boundary, Test Suite table, liboqs build, Key Management Lifecycle, QKD Pool
Model, 6G-Edge Network Model, EHR Workload Model, Metric Definitions) →
Experimental Methodology (Parameter Provenance table, Computational Cost,
Controlled/Independent Variables) → Results (Statistical Methodology, Figure
Design Notes, Successful Transmission Rate, Key-Establishment Latency, Latency
Distribution Shape, Communication Overhead, Summary Table) → Discussion
(Contribution Fulfillment, Ethical Considerations, Hypothesis Evaluation,
Oracle Policy Comparison, Go/No-Go Assessment, Overhead Interpretation) →
Limitations (Validity Taxonomy, Simulation-not-hardware, Network/QKD
simplifications, Threshold Sensitivity, Additional Implementation Findings,
Operational Data-Integrity Note) → Security Considerations (per-threat T1–T6,
Residual Risk Summary) → Future Work (Pre-Registered Statistical Plan,
Generalizability) → Conclusion (Returning to the Motivating Scenario,
Practical Implications) → Appendices (Full Pilot Results, Reproducibility,
Software Architecture, Pilot Configuration File) → Bibliography.

## 2. Current Architecture (as implemented in `src/`)

Nine logical components documented in the manuscript's Table "System
components": EHR Client/Application, IoMT/Healthcare Endpoint, 6G Access/Network
Layer, Healthcare Edge Gateway, Adaptive Security Layer, QKD Subsystem/Pool, PQC
Subsystem, Hospital/EHR Server, Key-Management Component. These map onto real
source modules:

- `src/crypto/` — classical (X25519/Ed25519), PQC (ML-KEM-768/ML-DSA-65 via
  liboqs), QKD pool, hybrid HKDF combiner, authentication
- `src/network/` — topology, per-hop channel model
- `src/workload/` — synthetic EHR transaction generator
- `src/adaptive/` — the controller implementing the mode-selection algorithm
- `src/baselines/` — B1–B5, one shared interface, one AEAD implementation
- `src/simulation/` — discrete-event harness (SimPy), per-transaction event
  records
- `src/metrics/` — raw-record collector, per-cell aggregator (percentiles,
  bootstrap CI)
- `src/utils/` — configuration loading, seed management

This matches the manuscript's Software Architecture appendix module table
exactly — no drift found between documented and actual module structure.

## 3. Current Baselines

Confirmed directly in `src/baselines/baselines.py` and the associated tests
(`tests/test_integration_scenarios.py`, `tests/test_b5_wait_path.py`):

- **B1** — Classical: X25519 ECDH + Ed25519 signatures
- **B2** — PQC-only: ML-KEM-768 + ML-DSA-65
- **B3** — QKD-only: QKD pool draw + ML-DSA-authenticated control channel; no
  fallback on pool exhaustion (raises, unconditional failure)
- **B4** — Static hybrid: QKD draw AND ML-KEM concurrently, combined via HKDF;
  no code path to PQC-only on QKD failure (verified: this is a structural
  property, not merely a configuration default)
- **B5** — Adaptive hybrid: controller (Algorithm 1) selects Hybrid or
  PQC-only per session based on QKD pool state and transaction criticality

This is the same five-baseline design specified in the master task's Part 10;
no baseline redefinition occurred in this project's history.

## 4. Current Experiment Design

`config/pilot.yaml` (verified verbatim, reproduced in the manuscript's new
appendix):

- 3 QKD availability levels: `{1.0, 0.5, 0.0}`
- 2 device counts: `{10, 1000}`
- 1 payload class: `medium`
- 1 network load: `nominal`
- 5 baselines: B1–B5
- 30 total configurations (3 × 2 × 1 × 1 × 5)
- `n_transactions_per_device: 10`, `sim_duration_seconds: 10.0`
- `repetitions_per_cell: 5`
- Adaptive thresholds: `pool_min_hybrid: 0.3`, `pool_min_wait: 0.1`,
  `wait_timeout_seconds: 0.05`
- `qkd_pool_sessions_buffer: 20` (capacity = 20 × 256 bits = 5,120 bits)
- `base_seed: 42`

A second config file, `config/full_experiment.yaml`, exists for a larger,
not-yet-run parameter sweep (a full study). It has **not** been executed;
only the pilot has produced results.

## 5. Current Dataset/Workload

The EHR workload is **not Synthea-based**. It is a procedural, synthetic,
FHIR-inspired generator in `src/workload/`, producing synthetic transaction
bodies with no real patient data. A dedicated regression test asserts the
absence of real-record-shaped fields. Payload size classes are configurable
(small 1–5KB, medium 20–80KB, large 200KB–1MB); the pilot used the medium
class exclusively. Three transaction types (read/write/share) are defined;
only `share` is exercised in the pilot. 5% of transactions are emergency-
criticality by default.

**Per the master task spec's Part 13 instruction:** Synthea was not
integrated into this experiment, and this audit does not pretend otherwise.
Integrating Synthea would require re-running the entire pilot against a
different workload generator — a new experiment, not a documentation change
— and is recorded here as a candidate future experiment, not performed in
this pass.

## 6. Current Results (independently re-traced against raw data)

Re-computed directly from `results/processed/pilot_summary.csv` and cross-checked
against `results/raw/pilot/*.jsonl` file count in this audit session:

- 30 cells confirmed (`wc -l` / distinct baseline × availability × device-count
  combinations)
- Sum of `n_transactions` across all 30 cells = **757,500** (matches manuscript)
- 150 raw `.jsonl` files confirmed present (5 repetitions × 30 cells)
- B4 at $a{=}0.0$, 1000 devices: success rate **0.002** (0.20%) — matches
  manuscript exactly
- B5 at $a{=}0.0$, 1000 devices: success rate **0.99684** (99.68%) — matches
  manuscript exactly
- B4/B5 mean latency and overhead figures at all three availability levels
  independently re-read from the CSV and match the manuscript's Table
  "Summary Table" and "Full Pilot Results" appendix to the reported precision

**No numerical discrepancy was found** between the manuscript's reported
pilot numbers and the raw/processed data files in this repository as of this
commit. See Section 9 below for the one caveat.

## 7. Current References

`paper/references/references.bib` — 16 entries, tiered [V]/[S]/[STD] per the
project's own verification-tier discipline (documented in the manuscript's
"Literature Verification Note" subsection). This session additionally
reviewed 7 externally supplied candidate references (Section 2 of the
master task); 2 were found directly relevant and verified in full ([V]-tier
equivalent), 1 marginally relevant (Tier 4, contextual only), and 3
irrelevant to this paper's subject matter. See the reference audit (Phase
2/3, pending completion of the external reference set) for the full
per-source breakdown.

`research/literature_matrix.csv` — 21 rows (20 candidate sources + header),
consistent with the manuscript's "Broader Literature Landscape" table, which
states 20 screened candidate sources.

## 8. Reproducibility Status

- Test suite: **61 tests, all passing** (`python3 -m pytest tests/ -q` →
  `61 passed in 1.50s`), matching the manuscript's stated test count exactly.
- Environment: Python **3.12.3** inside the project's `.venv` (note: the bare
  system `python3` reports 3.11.15 — this is expected and matches
  `docs/environment_manifest.md`'s documented practice of using the
  project-local virtualenv, not a discrepancy).
- Key dependency versions confirmed via `pip freeze` inside `.venv`:
  `liboqs-python==0.16.0`, `cryptography==50.0.0`, `matplotlib==3.11.1`,
  `numpy==2.5.2`, `pytest==9.1.1`, `simpy==4.1.2` — all match
  `requirements.lock.txt` and `docs/environment_manifest.md`.
- liboqs (C library) commit `8979276ad1eb008215aa78a3c56b3649f604bbb1`,
  version 0.16.0, documented with build instructions in
  `docs/environment_manifest.md`.
- Full pilot config (`config/pilot.yaml`) is version-controlled and matches
  the manuscript's appendix reproduction verbatim.

## 9. Numerical Discrepancies

One discrepancy of note, already caught and fixed **within this same
session** prior to this audit: the manuscript's Limitations section
("Operational Data-Integrity Note") previously described the metrics
collector as append-mode (a pre-fix behavior), which no longer matches the
actual code (`src/metrics/collector.py` opens its output file in `"w"`
truncate mode, confirmed by direct source inspection). This was corrected in
commit `543be66` before this audit began. No other discrepancy was found
between manuscript claims and repository state.

## 10. Citation Problems

- All 16 entries in the current bibliography were built under an explicit
  verification-tier discipline; no fabricated entries were found on
  inspection (author lists, years, and identifiers are either resolved DOIs
  or explicitly marked as unresolved with fields omitted rather than
  guessed).
- Two entries are `@misc` with `howpublished = {venue not independently
  confirmed}` — an intentional, honest downgrade rather than a fabrication,
  but these remain the two lowest-confidence citations in the bibliography
  and are flagged in Section 16.

## 11. Unsupported Claims

The manuscript already contains extensive self-flagging of its own
unsupported or partially-supported claims (Novelty Guardrails, Explicit
Security Claim Boundary, Contribution Fulfillment table marking C3 as
"Partially delivered"). No previously undisclosed unsupported claim was
found in this audit pass beyond what the manuscript itself already discloses.

## 12. Missing Experiments

- The full parameter sweep specified in `config/full_experiment.yaml` has not
  been run.
- No formal between-baseline hypothesis test (e.g., Mann-Whitney U) has been
  applied to any result — already disclosed in the manuscript's Limitations
  section.
- A Synthea-based workload has not been integrated or run (Section 5 above).
- An adaptive-threshold sensitivity sweep has not been run (the manuscript's
  "Threshold Sensitivity" subsection is explicitly qualitative/predictive,
  not measured).
- No hardware-timing (embedded/IoMT device) benchmark exists in this
  repository.

## 13. Missing Figures

The master task spec (Part 8) calls for 10 figures (architecture, sequence
diagram, state machine, key lifecycle, QKD/QBER model, threat model, 6G
topology, EHR pipeline, experimental framework, results trade-off). This
repository currently contains **3 figures**, all results plots generated
directly from `results/processed/pilot_summary.csv` via
`experiments/generate_figures.py`:

- `fig1_success_rate_vs_qkd_availability.{pdf,png}`
- `fig2_b5_latency_vs_qkd_availability.{pdf,png}`
- `fig3_overhead_by_baseline.{pdf,png}`

No architecture, sequence, state-machine, key-lifecycle, QKD-model, threat-
model, topology, workload-pipeline, or experimental-framework diagram
currently exists as a rendered figure — these concepts are covered in prose
and tables in the manuscript, not as diagrams. This is a genuine gap against
the master spec's Part 8/20 requirements.

## 14. Missing Tables

`paper/tables/` exists as an empty directory — the manuscript's tables are
authored inline in `main.tex` (LaTeX `table`/`table*` environments), not as
separate files. All tables the master spec calls for in Part 20 exist in
some form inline in the manuscript (components, crypto primitives, baselines,
experimental variables, workload/dataset statistics via the provenance
table, threat model, main results, reproducibility). No dedicated
statistical-comparison table (formal hypothesis-test results) exists, since
no formal hypothesis test has been run (Section 12).

## 15. Publication Risks

- **Architecture diagrams absent** (Section 13) — a reviewer expecting
  visual architecture/sequence/state-machine figures per common venue
  conventions will find prose and tables instead.
- **No formal statistical test** applied to any comparison — already
  disclosed, but remains a real methodological gap for a security/systems
  venue.
- **Two lowest-confidence bibliography entries** carry unconfirmed venues.
- **External reference set incomplete** — Phase 2/3 of this rewrite task is
  still waiting on additional files from the user before the full
  claim-citation matrix and bibliography cleanup can be finalized.
- **Full parameter sweep not run** — all quantitative claims rest on a
  30-configuration pilot explicitly labeled as a calibration study, not a
  completed systematic evaluation.

---

*This audit covers Phase 1 of the master rewrite task. Phase 2 (Drive/external
reference audit) is in progress and blocked on additional user-supplied
files. Phases 3–18 have not yet been started pending completion of Phase 2 and
user direction on which downstream phases to prioritize.*
