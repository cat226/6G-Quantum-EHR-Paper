# Phase 18: Publication-Readiness Gate

A RED / YELLOW / GREEN verdict against each criterion below, based on the
evidence produced across this project's full audit history (all in
`research/`), not on a fresh subjective read. GREEN means the criterion
is met with verified evidence. YELLOW means substantively addressed but
with a disclosed, non-blocking gap. RED means a real blocker to
submission.

**This document has been updated once since its original version** (a
follow-up compilation/figure/citation audit closed 3 of the original 5
YELLOW items — see "Changes since the original gate" below). The original
verdict and full punch list are preserved in git history
(`git log -- research/publication_readiness_gate.md`) rather than erased.

| Criterion | Verdict | Evidence |
|---|---|---|
| Manuscript compiles cleanly | **GREEN** | 37 pages, zero LaTeX errors, zero undefined references/citations (verified on a clean-slate recompile: aux/bbl/blg/log/out removed and rebuilt from nothing) |
| Citation integrity (no orphans/dangling, no citation-dumping) | **GREEN** | 190 claim-citation rows, all 126 bib entries cited, zero orphans, zero dangling, zero duplicate keys (`research/claim_citation_matrix.csv`, `research/citation_integrity_report.md`) |
| Citation honesty (no fabricated authors/venues/DOIs) | **YELLOW --- environment-blocked, not actionable from here** | Every entry is tiered [V]/[S]/[STD] and the tiering is honest; 114 [S]-tier entries are formally enumerated with their exact supporting claims in `research/unverified_references.md`. A full [V]-tier pass (independently fetching and confirming every [S] entry) requires external network access this sandboxed environment's egress policy blocks for essentially all external domains --- this is a tooling constraint, not undone work |
| Experimental data matches raw results | **GREEN** | 80+ checks against `results/processed/pilot_summary.csv` across two independent audit passes; one discrepancy found and corrected (payload-encryption-cost range); zero discrepancies in the follow-up pass (`research/numerical_consistency_report.md`) |
| Reproducibility | **GREEN** | 62/62 tests passing (re-run this session), pinned environment (Python 3.12.3, liboqs 0.16.0 commit `8979276`), full pilot config reproduced verbatim in the manuscript appendix, and a complete tested command sequence in `REPRODUCIBILITY.md` |
| Figures present and rendering | **GREEN** (was YELLOW) | All 6 content figures complete: the architecture diagram (previously a blank placeholder) now shows every required component with a 5-path legend; the sequence diagram was corrected to match the actual implementation (see below); all 3 results figures regenerated from source and confirmed pixel-identical to the checked-in files |
| Internal numerical consistency (tables vs. prose vs. figures) | **GREEN** | Overhead byte counts, latency figures, and the notation table all cross-check exactly against Table `tab:environment`'s measured primitive sizes; figure values confirmed to trace to the same source CSV as table values |
| Cross-reference integrity | **GREEN** | Zero broken `\ref`/`\label` pairs |
| Terminology/notation consistency | **GREEN** (was YELLOW) | The $a$/$\qkdavail$ overlap is resolved: the configured pilot sweep parameter now has its own symbol ($a_{\text{cfg}}$, `\acfg`), distinct from the controller's instantaneous pool fraction ($\qkdavail$), with a clarifying notation-table entry |
| Honest self-critique present | **GREEN** | Manuscript contains its own Limitations section, Contribution Fulfillment table, Go/No-Go criteria table, and Hypothesis Summary table scoring its own claims against results |
| Simulated peer review | **GREEN**, 1 item remains open by design | 9 reviewer concerns simulated across 3 disciplinary perspectives; 8 addressed (7 originally, plus R1.3 below), 1 remains open as a suggested (non-blocking) clarification (R3.1: dataset-realism justification for a healthcare-informatics audience) |
| Test coverage of safety-critical code paths | **GREEN** (was YELLOW) | `tests/test_pqc.py::test_ml_kem_shared_secret_mismatch_raises` now directly exercises the ML-KEM fail-loud guard via monkeypatching `decap_secret`; verified meaningful by confirming it fails when the guard is manually disabled, then restoring the guard |
| Diagram/implementation correctness | **GREEN** (new criterion, not in the original gate) | The message sequence diagram and its supporting prose previously showed the mode-sync authentication round trip occurring *after* key derivation, with only one round trip total. Direct inspection of `src/baselines/baselines.py`'s `B5Adaptive.establish_session_key()` found the actual order is mode-sync *first*, then key derivation, then a *second*, separate session-establish round trip. Both the diagram and prose were corrected to match the implementation, per this audit's own rule that code is authoritative over diagrams |
| Version control / provenance | **YELLOW --- environment-blocked, not actionable from here** | All work committed locally on `claude/pensive-bohr-1rdrrp` (clean history, descriptive commits) but not pushed to GitHub --- blocked by an org-level Claude GitHub App access gap (`cat226/6G-Quantum-EHR-Paper` returns 403 on every push attempt, re-confirmed repeatedly). Requires an org admin to install the app, or the user to reconnect GitHub; not resolvable by further work in this session |

## Overall verdict: **GREEN, with 2 environment-blocked items outside this session's control**

Every criterion that more auditing, verification, or engineering work
could actually close has been closed. The two remaining YELLOW items are
not unfinished work — they are blocked by this sandboxed environment's
network egress policy (external citation verification) and GitHub access
grant (push), respectively, and would resolve immediately given either:

1. External network access, to independently fetch and confirm the 114
   `[S]`-tier bibliography entries (already honestly disclosed and
   individually mapped to their claims in `research/unverified_references.md`
   in the meantime).
2. GitHub access for this environment/organization, to push the 27+
   local commits already sitting on `claude/pensive-bohr-1rdrrp`.

## Changes since the original gate

The original gate (preserved in git history) listed 5 YELLOW items and 1
GREEN-with-caveat item. A follow-up compilation/figure/citation audit
closed 3 of the 5:

1. ~~Fill in Figure 1~~ --- **done**: full publication-quality TikZ
   architecture diagram with a 5-path legend, replacing the blank
   placeholder.
2. ~~Add a test that actually triggers the ML-KEM shared-secret mismatch
   guard~~ --- **done**: `test_ml_kem_shared_secret_mismatch_raises`,
   verified meaningful.
3. Push the branch to GitHub --- **still blocked**, environment-level, not
   actionable from this session.
4. ~~Resolve the $a$/$\qkdavail$ notational overlap~~ --- **done**:
   introduced `\acfg` as a distinct symbol for the configured sweep
   parameter.
5. A full [V]-tier verification pass on the [S]-tier bibliography entries
   --- **still blocked**, environment-level (no external fetch access),
   not actionable from this session; the disclosure itself
   (`research/unverified_references.md`) is complete.

One item beyond the original 5 was found and fixed during the follow-up
audit and is not in the original list: the message-sequence diagram and
Data Flow prose's ordering discrepancy against the actual implementation
(see the "Diagram/implementation correctness" row above).
