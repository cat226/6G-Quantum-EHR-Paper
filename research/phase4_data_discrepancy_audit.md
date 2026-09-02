# Phase 4: Experimental-Data Discrepancy Audit

Every quantitative claim in `main.tex`'s Results section (`sec:results`) and
its Appendix full-results table (`app:fulltable`, Table `tab:fulldata`) was
re-derived programmatically from the raw processed pilot data
(`results/processed/pilot_summary.csv`, itself aggregated from the 151
per-repetition JSONL files under `results/raw/pilot/`) and diffed against
the number printed in the manuscript. This document is the record of that
check, not manuscript content.

## Method

A Python script (`verify_results.py`, not checked into the repo --- a
scratch audit tool, not a project artifact) loaded `pilot_summary.csv`,
looked up each of the 30 `(baseline, qkd_availability, device_count)` cells,
and compared every number the manuscript states against the corresponding
CSV field, with a tolerance tight enough to catch a wrong reported digit
(typically ±0.00006 for 4-decimal figures, ±0.0006 for 3-decimal figures)
but loose enough to allow for the manuscript's stated rounding.

80 individual value-checks were run, covering:

- All 15 rows of the 1{,}000-device summary table (`tab:summary`): success
  rate, \keyest\ mean latency, overhead bytes, fallback frequency.
- All 30 rows of the full-results appendix table (`tab:fulldata`): success
  count, \keyest\ mean, end-to-end mean, fallback frequency, for every
  baseline × availability × device-count cell (checked separately, see
  below).
- Every specific number quoted in prose in "Successful Transmission Rate,"
  "Key-Establishment Latency," "Latency Distribution Shape," and
  "Communication Overhead" (success counts/percentages, mean/median/p95
  latencies, fallback-frequency percentages, the ~11.4ms network-transit
  offset, the per-baseline overhead byte counts).

## Findings

**29 of 30 checked quantities matched exactly** (within stated rounding).
**One discrepancy was found and corrected in the manuscript** (commit
following this audit):

> **Payload encryption cost range.** The Results section claimed AES-256-GCM
> payload-encryption cost is "essentially constant across every condition,
> 0.036ms--0.043ms regardless of baseline, availability, or device count."
> The actual range across all 30 pooled cells is **0.0278ms--0.0432ms** ---
> the claimed lower bound (0.036ms) excluded most of the 10-device cells,
> whose per-transaction encryption cost sits systematically lower than the
> 1{,}000-device cells (plausibly a batching/amortization or measurement-
> granularity effect at low transaction counts, not investigated further
> here since it does not change the section's actual claim --- that
> encryption cost does not explain the \keyest-driven latency variation).
> **Fix applied:** the sentence now states the true full range
> (0.028ms--0.043ms) and notes the 10-device/1{,}000-device split
> explicitly, rather than silently narrowing the range to only the subset
> that fit the original claim.

No other numerical claim in the Results section or its appendix table
required correction. In particular, all of the following were independently
re-derived and matched exactly:

- The B3/B4 near-identical collapse at `a=0.0`, 1{,}000 devices (100/50{,}000
  each, 0.20% each) and B5's contrast (49{,}842/50{,}000, 99.68%).
- The `a=0.5` figures (B3: 25{,}018/50{,}000, 50.04%; B4: 25{,}033/50{,}000,
  50.07%; B5: 49{,}862/50{,}000, 99.72%).
- Every \keyest\ mean latency figure at all three availability levels and
  both device counts, for both B4 and B5.
- The bimodal-distribution finding (B5, 1{,}000 devices, `a=0.0`: mean
  47.877ms vs. median 50.384ms vs. p95 50.629ms) and its `a=0.5` and `a=1.0`
  counterparts.
- The end-to-end median/p95 figures and the ~11.4ms network-transit offset.
- All five baselines' communication-overhead byte counts (96 / 5{,}581 /
  3{,}309 / 5{,}581 / 8{,}890), confirmed constant across every availability
  level and device count within each baseline.
- All 30 rows of the full-results appendix table, checked cell-by-cell
  against `n_success`, `n_transactions`, `key_establishment_ms_mean`,
  `end_to_end_ms_mean`, and (for B5) `fallback_frequency`.

## Cross-reference

This audit complements, and does not replace,
`research/paper_rewrite_audit.md` (Phase 1), which covers structural,
citation, and reproducibility concerns rather than a systematic numeric
re-derivation of every Results-section figure.
