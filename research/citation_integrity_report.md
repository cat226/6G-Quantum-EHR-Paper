# Citation Integrity Report

Programmatic audit of `paper/manuscript/main.tex` against
`paper/references/references.bib`. Method: regex-extract every `\cite{}`
key from the manuscript and every `@type{key,` from the bib file, then
compute set differences and per-entry field completeness. Script is not
checked into the repo (a scratch audit tool, re-runnable from this
description, not project content).

## Summary counts

| Metric | Value |
|---|---|
| Total unique citation keys used in manuscript | 126 |
| Total bibliography entries | 126 |
| Citations used but missing from bibliography | **0** |
| Bibliography entries never cited | **0** |
| Duplicate BibTeX keys | **0** |
| Malformed entries (missing required field) | **2** |
| Entries with no `author` field | 78 |

**Compilation gate: PASS.** No cited key lacks a bibliography entry, so
there is no condition under which this repository's bibliography would
cause an undefined-citation compilation failure. Confirmed independently
by the pdflatex/bibtex build log: zero `Citation ... undefined` warnings.

## Malformed entries (missing `year` field)

Two `@misc` entries lack a `year` field, which IEEEtran's bibliography
style needs to render a complete citation:

1. **`aguilarmelchor2018hqc`** (cites the HQC origin paper). This entry
   carries an internal inconsistency worth flagging explicitly rather than
   silently resolving: its key encodes "2018," but its `howpublished`
   field gives an arXiv identifier, `arXiv:1612.05572` --- the `1612`
   prefix is arXiv's own year-month encoding for **December 2016**, not
   2018. The entry also mixes a `journal` field with `howpublished`,
   which is itself irregular BibTeX usage (suggesting an eventual journal
   publication distinct from the arXiv preprint, at an unconfirmed date).
   **No year was inserted.** Filling in either 2016 or 2018 without
   independently confirming which date corresponds to which
   publication venue would risk exactly the fabrication this audit
   exists to prevent.
2. **`etsi2018whitepaper27`** (cites ETSI White Paper No. 27,
   "Implementation Security of Quantum Cryptography"). No internal
   conflict exists here (no second date-bearing field to contradict the
   key), but the year is still not asserted in a `year` field, only
   implied by the key name. **No year was inserted**, on the same
   principle: the key name reflects what a past research pass believed at
   entry-creation time, not an independently reconfirmed fact.

Both are logged in `research/unverified_references.md` with the specific
disposition recommended for each (see that file). Neither entry's
underlying manuscript claim depends on the exact publication year: the
HQC citation supports "NIST's fourth round selected HQC" (independently
corroborated by the separately-cited `nist2025pqcround4status`), and the
ETSI citation supports "ETSI published a technical assessment," not a
date-sensitive claim. No manuscript prose was changed as a result --- the
issue is bibliographic completeness, not a substantive claim at risk.

## Entries with no `author` field (78 of 126)

This is **not** a defect --- it is this project's own stated, deliberate
policy (see the manuscript's own "Literature Verification Note" in
Related Work): where a full author list could not be independently
confirmed, the field is omitted rather than guessed. All 78 are tiered
`[S]` (found via live search, real specific metadata, not independently
re-fetched) in the bib file's own section comments. IEEEtran renders these
correctly (title-first formatting, confirmed in `main.bbl`), with no
placeholder or broken-looking output. Listed here for completeness per
this audit's request, not flagged as an error.

## Suspicious/incomplete entries beyond the above

No entry was found with a fabricated-looking DOI, an inconsistent
title/venue pairing, or any other structural red flag beyond the two
missing-year cases above. Every entry's `note` or `howpublished` field
(arXiv ID, PMC ID, standards-document number, or venue name) is a
concrete, checkable identifier, not a vague placeholder.

## Cross-reference to prior audits

This report formalizes and re-confirms, with a fresh independent script
run, the same zero-orphan/zero-dangling result first established in
`research/claim_citation_matrix.csv` (Phase 3) and re-confirmed in
`research/consistency_audit.md` (Phase 17). The two malformed-year entries
were not previously called out as a distinct category in either document;
this is the first pass to check bib entries for field completeness
specifically, rather than only citation-key set membership.
