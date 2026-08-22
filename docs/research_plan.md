# Research Plan

**Project:** 6G-Enabled Hybrid Quantum-Secure Architecture for Electronic
Health Record Sharing
**Authors:** Ramana Sree K V, Verona Ann Mariya
**Status:** Workspace initialized. No research, literature review, or
writing has begun yet.

## Purpose of this document
Track the phased plan for this project. Update as decisions are made —
this is a living document, not a fixed schedule.

## Planned Phases (high level, TODO: refine dates/scope)

1. **Workspace initialization** — ✅ done (this step).
2. **Literature collection** — TODO (not started).
   - Search venues (IEEE Xplore, ACM DL, arXiv, Scopus, etc. — TODO confirm access).
   - Populate `research/literature_matrix.csv` with verified entries only.
   - No entry should be added without a checkable DOI/URL.
3. **Research gap synthesis** — TODO (not started).
   - Populate `research/research_gaps.md` from the literature matrix.
4. **Architecture design** — TODO (not started).
   - Design the proposed hybrid PQC + QKD + 6G + edge architecture for EHR sharing.
   - Must be clearly labeled as a proposal until validated.
5. **Methodology definition** — TODO (not started).
   - Decide simulation tools (see `simulation/` subfolders: 6g, pqc, qkd).
   - Decide evaluation metrics and baselines.
6. **Experimentation / simulation** — TODO (not started).
   - Implement in `experiments/src/`, configs in `experiments/configs/`.
   - Store raw outputs in `experiments/results/`, figures in `experiments/plots/`.
   - No results may be reported until they are actually produced by code
     in this repository.
7. **Security analysis** — TODO (not started).
   - Threat modeling, formal/informal security argument.
8. **Writing** — TODO (not started, explicitly deferred per project instructions).
   - Sections filled in only as their supporting work is completed.
9. **Review and validation** — TODO.
   - Cross-check all claims against source data/results before submission.

## Open decisions (to resolve before proceeding)
- [ ] Target venue / journal and its formatting & page requirements.
- [ ] Which 6G network simulator (ns-3, custom discrete-event model, etc.).
- [ ] Which PQC library/scheme(s) (e.g., liboqs / Kyber / Dilithium).
- [ ] Which QKD simulation approach (Qiskit-based protocol simulation vs.
      other tools).
- [ ] Whether any real/public EHR-related dataset will be used, and if so,
      its licensing and ethics considerations.
- [x] Definition of "hybrid" for this architecture — not yet finalized,
      but Task 2 recorded a provisional, feasibility-driven working
      default (Option C: QKD-primary, PQC-authenticates-and-falls-back)
      to guide literature search terms; final choice deferred to
      Task 5+ evidence. See `docs/task_logs/TASK02_research_question_and_contributions.md`.
- [x] Literature matrix schema — reconciled and finalized during Task 3
      setup; see `docs/task_logs/TASK03_04_search_methodology_and_matrix_schema.md`.

## Blocker from Task 3 setup — RESOLVED
The "no literature search capability" blocker flagged at the start of
Task 3 was resolved in a subsequent, search-enabled session. Real,
search-verified literature work was produced there and has been
integrated into this repo:
- `docs/task_logs/TASK03_04_synthesis.md` — 20-paper verified/partially-
  verified batch (not yet the full 30–50 target)
- `research/literature_matrix.csv` — populated with those 20 papers
  (schema unchanged from the reconciled Task 3 schema)
- `paper/references/references_verified_only.bib` — 3 fully-verified
  entries (Devaraj et al. 2026; Frontiers 2026 PQC-healthcare review;
  MDPI Computers 2026 IoMT-auth review); 17 further candidates remain
  `PARTIAL` and are deliberately excluded from this file until fetched
  and confirmed
- `docs/task_logs/TASK05_novelty_collision_analysis.md` — a second,
  targeted live-search pass checking specific "closely related work"
  claims (11 further papers, P1–P11 numbering, distinct from the P01–P20
  numbering in `literature_matrix.csv` — **do not conflate the two
  numbering schemes**; cross-reference by author/year/title instead)
- `docs/task_logs/TASK05_research_gap_and_blueprint.md` — the resulting
  gap analysis, direction selection (Direction E), and locked research
  blueprint (title, RQ, hypotheses, contributions, baselines, metrics,
  threat model)

## Task 5 outcome — LOCKED (approved)
**Title:** "Latency-Aware Adaptive QKD-PQC Key Establishment for
Electronic Health Record Sharing in 6G-Edge Healthcare Networks: A
Simulation-Based Evaluation Under Varying QKD Availability"

**Core RQ:** How does an adaptive QKD-PQC key-establishment mechanism —
falling back toward PQC-only operation as simulated QKD availability
decreases — affect key-establishment latency, end-to-end EHR
transmission latency, communication overhead, and successful-transmission
rate, relative to classical, PQC-only, QKD-only, and static-hybrid
baselines, across varying QKD availability levels and device/user counts
in a 6G-edge healthcare network topology?

Standing caveat carried forward from Task 5: this rests on ~25 targeted
live searches across two sessions, not the full 30–50 paper systematic
pass Task 3 originally specified. Several load-bearing papers (Roosan et
al. 2025; Papadopoulos et al. 2026; Spooren et al. 2026; Atutxa & Sanz et
al. 2025; Zhu 2025) are cited at "found and cross-checked via live search"
confidence, not full-text-verified per the Task 3 checklist. Anything
design-critical resting on them is marked as a DESIGN ASSUMPTION, not an
established fact, in downstream task outputs (starting with Task 6).

## Explicit constraints (per project instructions)
- Do not fabricate citations, datasets, experiments, or results.
- Do not assume the architecture is already implemented.
- Do not begin literature collection or manuscript writing until
  explicitly instructed.
