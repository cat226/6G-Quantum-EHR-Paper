# Phase 17: Terminology, Notation, and Cross-Reference Consistency Audit

A systematic pass checking the manuscript for internal consistency: does it
use one name for one thing throughout, do all cross-references resolve, and
does notation mean the same thing everywhere it appears. Findings below are
graded by severity; nothing here required correcting an incorrect number
(that was Phase 4's job) --- this is purely about naming and referencing.

## 1. Cross-reference integrity (checked programmatically)

- **71 `\label{}` definitions, 55 `\ref{}` uses.** Every `\ref` resolves to
  an existing `\label` --- zero broken references.
- **16 labels are never `\ref`'d elsewhere** (`app:architecture`,
  `app:config`, `app:fulltable`, five `eq:` labels, `fig:architecture`,
  `fig:decisionflow`, `fig:sequence`, `sec:anticipatedrisks`,
  `sec:background`, `sec:gonogo`, `sec:pqcoverheadlit`, `sec:provenance`).
  This is not a defect: a label exists so a section/figure/equation *can*
  be referenced, not because it must be. Spot-checked several: the three
  new TikZ figures' labels are legitimate (their captions are
  self-contained and don't need in-text pointers), and the `eq:` labels
  are on equations introduced and used in the same paragraph, where
  re-pointing to them by number would be more awkward than useful prose.
- **All 126 bibliography entries are cited; all cited keys exist in the
  bibliography** (re-confirmed here, first established in Phase 3).

## 2. Terminology

- **"key establishment" vs. "key-establishment"**: both forms appear (6 and
  7 occurrences respectively outside the `\keyest` macro, which always
  renders hyphenated). Checked each occurrence's grammatical role: the
  hyphenated form is used exclusively as a compound adjective before a
  noun ("key-establishment logic," "key-establishment strategy,"
  "key-establishment focus"), and the unhyphenated form exclusively as a
  standalone noun phrase ("key establishment is...", "hybrid key
  establishment"). This follows standard English compounding convention
  correctly rather than being an inconsistency --- **no change needed**.
- **Baseline naming (B1--B5)**: used consistently throughout prose,
  tables, and figures; no baseline is ever referred to by an alternate
  name or abbreviation. Confirmed against `src/baselines/baselines.py`
  class names (`B1Classical`, `B2PQCOnly`, `B3QKDOnly`, `B4StaticHybrid`,
  `B5Adaptive`) --- the paper's B1--B5 labels match the
  implementation's own naming exactly, not a renamed or reordered mapping.
- **Acronym first-use discipline**: EHR, PQC, QKD, HNDL, and CRQC are each
  spelled out in full with the acronym in parentheses at first use
  (Abstract and/or Introduction), and Table `tab:glossary` additionally
  collects all acronyms in one place for reference. No acronym is used
  before being defined.

## 3. Notation

- **Table `tab:notation`** is internally consistent with its own listed
  symbols' usage in Algorithm 1, Section~`sec:qkdmodel`, and the Worked
  Example --- $\tau_{\text{hybrid}}$, $\tau_{\text{wait}}$, $T_{\text{wait}}$,
  $L$, $C$, $r$, $\Delta t$ all mean the same thing everywhere they are used.
- **One overlap worth flagging (minor, not an error):** the symbol $a$ is
  used for two related but distinct quantities that happen to render
  identically. `\qkdavail` (defined as `\ensuremath{a}`) denotes the
  controller's *instantaneous* normalized pool fraction $L/C \in [0,1]$,
  the actual input Algorithm 1 consumes (Section~`sec:adaptive`,
  Section~`sec:qkdmodel`). Separately, the Experimental Methodology,
  Results, and Discussion sections use literal `$a$` for the *configured
  nominal QKD availability level* swept across the pilot (0.0, 0.5, 1.0)
  --- an experimental-design parameter that sets the pool's generation
  rate, not the instantaneous fraction itself. The two are related (the
  configured level determines the steady-state value the instantaneous
  fraction fluctuates around) but are not the same variable, and the
  manuscript never states this distinction explicitly --- a careful reader
  moving from Algorithm 1 to Table `tab:summary` could momentarily read
  "$a=0.5$" as "the controller's pool fraction was exactly 0.5," which is
  not quite what it means. **Recommended fix (not applied here, since it
  touches the notation table and multiple sections and is a judgment call
  the authors should make directly):** either introduce a second symbol
  for the configured sweep parameter (e.g., $a_{\text{cfg}}$) or add one
  clarifying sentence at first use in Section~`sec:methodology` stating
  that the configured level determines the generation rate the
  instantaneous $\qkdavail$ is drawn against, not a fixed value $\qkdavail$
  holds throughout a transaction.

## 4. Figure/table caption self-containedness

Spot-checked all 3 new TikZ figures and the 3 results figures: each
caption states what the figure shows without requiring the reader to have
just read the preceding paragraph, consistent with IEEE style expectations.

## 5. Overall verdict

No cross-reference is broken, no citation is orphaned or dangling, baseline
and acronym naming is fully consistent, and the one notational overlap
found ($a$ / $\qkdavail$) is a genuine but minor clarity issue rather than
an error --- the two quantities are never actually confused with each
other in context, only potentially ambiguous to a reader moving quickly
between sections. This is left as a recommendation rather than an
unrequested edit to notation the authors may have reasons to keep as-is.
