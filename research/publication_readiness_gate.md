# Phase 18: Publication-Readiness Gate

A RED / YELLOW / GREEN verdict against each criterion below, based on the
evidence produced across Phases 1--17 of this audit (all in `research/`),
not on a fresh subjective read. GREEN means the criterion is met with
verified evidence. YELLOW means substantively addressed but with a
disclosed, non-blocking gap. RED means a real blocker to submission.

| Criterion | Verdict | Evidence |
|---|---|---|
| Manuscript compiles cleanly | **GREEN** | 37 pages, zero LaTeX errors, zero undefined references/citations (verified this session, full pdflatex/bibtex/pdflatex/pdflatex cycle) |
| Citation integrity (no orphans/dangling, no citation-dumping) | **GREEN** | Phase 3: 190 claim-citation rows, all 126 bib entries cited, zero orphans, zero dangling (`research/claim_citation_matrix.csv`) |
| Citation honesty (no fabricated authors/venues/DOIs) | **YELLOW** | Every entry is tiered [V]/[S]/[STD] and the tiering is honest --- but only a minority of the 126 entries are [V] (independently fetched/confirmed); most are [S] (real, specific search-result metadata, not independently re-verified against full text). This is disclosed prominently in the manuscript's own "Literature Verification Note" and is not a fabrication risk, but a full [V]-tier pass (fetching and confirming every [S] entry) was not possible in this environment (network egress to most external sources is blocked) and remains outstanding |
| Experimental data matches raw results | **GREEN** (after one fix) | Phase 4: 80 checks against `results/processed/pilot_summary.csv`; 29/30 matched exactly, 1 corrected (payload-encryption-cost range) |
| Reproducibility | **GREEN** | 61/61 tests passing (re-run this session), pinned environment (Python 3.12.3, liboqs 0.16.0 commit `8979276`), full pilot config reproduced verbatim in the manuscript appendix |
| Figures present and rendering | **YELLOW** | 5 of 6 content figures are complete and render correctly (sequence diagram, decision-flow diagram, 3 results figures from real data). Figure 1 (system architecture) is currently a **blank placeholder box** at the user's explicit request, reserving layout space for an image to be inserted later --- this must be filled before submission |
| Internal numerical consistency (tables vs. prose vs. figures) | **GREEN** | Phase 4 plus this phase's spot-checks: overhead byte counts, latency figures, and the notation table all cross-check exactly against Table `tab:environment`'s measured primitive sizes |
| Cross-reference integrity | **GREEN** | Phase 17: zero broken `\ref`/`\label` pairs |
| Terminology/notation consistency | **YELLOW** | Phase 17: one minor, non-blocking notational overlap flagged ($a$ used for both the controller's instantaneous pool fraction and the experiment's configured sweep parameter) --- recommended but not applied, since it is the authors' call |
| Honest self-critique present | **GREEN** | Manuscript already contains its own Limitations section, Contribution Fulfillment table, Go/No-Go criteria table, and Hypothesis Summary table scoring its own claims against results, including at least one hypothesis marked incomplete by the authors' own design |
| Simulated peer review | **GREEN**, with 2 open items | Phase 16: 9 reviewer concerns simulated across 3 disciplinary perspectives; 7 already addressed in the manuscript's existing text, 2 genuinely open (see below) |
| Test coverage of safety-critical code paths | **YELLOW** | The ML-KEM shared-secret-mismatch fail-loud guard (`src/crypto/pqc.py`) exists and is architecturally sound, but Phase 16's review found no test in the 61-test suite that actually triggers it (the test with a matching name instead exercises a QKD pool-capacity failure) |
| Version control / provenance | **YELLOW** | All work is committed locally on `claude/pensive-bohr-1rdrrp` (clean history, descriptive commits) but **not pushed to GitHub** --- blocked throughout this session by an org-level Claude GitHub App access gap (`cat226/6G-Quantum-EHR-Paper` returns 403 on every push attempt). Not resolvable from this session; requires an org admin to install the app, or the user to reconnect GitHub |

## Overall verdict: **YELLOW**

Nothing found across 18 phases of audit constitutes a correctness blocker
in the sense of a wrong claim, a fabricated citation, or a broken build.
The paper is honest, internally consistent, and its central empirical
result (the B4/B5 divergence under QKD unavailability) is verified against
raw data to the decimal place. What keeps this at YELLOW rather than GREEN
is a short, concrete, non-fabrication punch list:

1. **Fill in Figure 1** (architecture diagram) --- currently blank by
   explicit user request; trivial to restore from git history
   (`git show d80e808:paper/manuscript/main.tex`) if the original TikZ
   version is wanted back, or replace with a professionally drawn image.
2. **Add a test that actually triggers the ML-KEM shared-secret mismatch
   guard**, rather than relying on a same-named test that covers a
   different failure mode.
3. **Push the branch to GitHub** once org access is restored, so the work
   is not only local to this session's container.
4. (Optional, not blocking) Resolve the $a$/$\qkdavail$ notational overlap
   with one clarifying sentence.
5. (Optional, not blocking) A full [V]-tier verification pass on the
   [S]-tier bibliography entries, if and when external fetch access is
   available --- the current [S] tiering is honest and disclosed, not a
   defect, but upgrading it would strengthen the paper further.

None of these require touching the paper's substantive claims, results,
or writing --- they are closeout items, not revisions.
