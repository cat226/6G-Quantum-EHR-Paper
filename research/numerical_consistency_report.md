# Numerical Consistency Report

Cross-checks every headline numerical claim across four independent
surfaces — manuscript prose, manuscript tables, manuscript figures, and
the raw/processed result files those figures and tables are built from —
for the same underlying quantity. This extends, and cross-references
rather than duplicates, `research/phase4_data_discrepancy_audit.md`
(which ran 80 prose/table checks against raw data but did not separately
check figure values, since at that time the figures had not yet been
independently regenerated and pixel-diffed against source).

## Method

- **Source data**: `results/processed/pilot_summary.csv` (30 rows, one per
  baseline x QKD-availability x device-count cell, pooled across 5
  repetitions), itself aggregated from 150 raw JSON-lines files under
  `results/raw/pilot/` by `experiments/analyze_pilot.py`.
- **Figure values**: `paper/figures/fig{1,2,3}_*.pdf`/`.png`, regenerated
  in this audit pass directly from `pilot_summary.csv` via
  `experiments/generate_figures.py` and confirmed **pixel-identical**
  (zero-diff, `ImageChops.difference` bounding box `None`) to the
  previously checked-in figures — i.e., the checked-in figures are
  provably unedited outputs of that script against that data, not
  manually altered.
- **Table values**: `paper/manuscript/main.tex`, Table `tab:summary`
  (1,000-device subset) and Table `tab:fulldata` (all 30 configurations).
- **Manuscript prose**: the Results section's narrative claims.

## Consolidated table

| Claim | Source data (raw CSV cell) | Manuscript prose value | Table value | Figure value | Status |
|---|---|---|---|---|---|
| B4 collapses to ~0.20% success at $a_{\text{cfg}}=0.0$, 1,000 devices | `B4, qkd=0.0, dev=1000`: 100/50000 = 0.0020 | "0.20%, 100/50,000" | `tab:summary`: 0.0020; `tab:fulldata`: 100/50000 | fig1: B4 point visually at ~0% (1,000-devices panel, $a_{\text{cfg}}=0$) | MATCH |
| B3 collapses identically to B4 at the same cell | `B3, qkd=0.0, dev=1000`: 100/50000 = 0.0020 | "0.20%, 100/50,000, indistinguishable to three sig. figs." | `tab:summary`: 0.0020; `tab:fulldata`: 100/50000 | fig1: B3 (gray) traces B4 (red) almost exactly, per caption | MATCH |
| B5 sustains ~99.68% at the same cell | `B5, qkd=0.0, dev=1000`: 49842/50000 = 0.99684 | "99.68%, 49,842/50,000" | `tab:summary`: 0.9968; `tab:fulldata`: 49842/50000 | fig1: B5 (blue) at ~100% across all $a_{\text{cfg}}$ | MATCH |
| B3/B4 at $a_{\text{cfg}}=0.5$, 1,000 devices | B3: 25018/50000=0.50036; B4: 25033/50000=0.50066 | "B3 50.04%, B4 50.07%" | `tab:summary`: B3 0.5004, B4 0.5007; `tab:fulldata` matches | fig1: both trace the ~50% midpoint | MATCH |
| B5 mean \keyest\ at $a_{\text{cfg}}=1.0$ (10 / 1,000 devices) | 0.438004 / 0.432288 ms | "0.4380ms / 0.4323ms" | `tab:summary`: 0.4323 (1000-dev row); `tab:fulldata`: 0.4380 / 0.4323 | fig2: rightmost points, both series converge near y$\approx$0.43 on log axis | MATCH |
| B4 mean \keyest\ at $a_{\text{cfg}}=1.0$ (10 / 1,000 devices) | 0.255571 / 0.262593 ms | "0.2556ms / 0.2626ms" | `tab:summary`: 0.2626 (1000-dev row); `tab:fulldata`: 0.2556 / 0.2626 | (B4 not plotted in fig2, which is B5-only by design, stated in caption) | MATCH |
| B5 mean \keyest\ at $a_{\text{cfg}}=0.5$ (10 / 1,000 devices) | 32.8894 / 45.5832 ms | "32.89ms / 45.58ms" | `tab:summary`: 45.583 (1000-dev row); `tab:fulldata`: 32.8894 / 45.5832 | fig2: middle points, ~30-45ms band | MATCH |
| B5 mean \keyest\ at $a_{\text{cfg}}=0.0$ (10 / 1,000 devices) | 40.2358 / 47.8768 ms | "40.24ms / 47.88ms" | `tab:summary`: 47.877 (1000-dev row); `tab:fulldata`: 40.2358 / 47.8768 | fig2: leftmost points, ~40-48ms band | MATCH |
| B5 fallback frequency, full range | 0.0% ($a_{\text{cfg}}=1.0$) to 3.2/4.7% ($a_{\text{cfg}}=0.5$) to 85.0/99.85% ($a_{\text{cfg}}=0.0$) | stated exactly as listed | `tab:summary`: 0.0000/0.0470/0.9985 (1000-dev); `tab:fulldata`: all 6 cells match | (fallback frequency not separately plotted; reported only in text/tables) | MATCH |
| Communication overhead by baseline | B1=96, B2=5581, B3=3309, B4=5581, B5=8890 bytes, constant across all 30 cells | stated exactly, with byte-level derivation from Table `tab:environment` | `tab:summary`/`tab:fulldata`: all rows per baseline match exactly | fig3: bars at 96/5,581/3,309/5,581/8,890, value labels generated programmatically from the same CSV column | MATCH |
| B5 bimodal distribution, $a_{\text{cfg}}=0.0$, 1,000 devices | mean 47.876812, median 50.384315, p95 50.629250 | "mean 47.877ms, median 50.384ms, p95 50.629ms" | not separately tabulated (prose-only finding) | (not separately plotted; fig2 shows mean+CI only) | MATCH |
| Payload AES-256-GCM encryption cost range | min 0.027783ms (B3,10dev,$a=1.0$) to max 0.043227ms (B5,1000dev,$a=0.0$), across all 30 cells | "0.028ms--0.043ms" (**corrected in Phase 4** from an original, narrower "0.036--0.043ms" that covered only the 1,000-device subset) | not tabulated | not plotted | MATCH (post-correction) |
| 757,500 total simulated transactions | 15 cells x 500 + 15 cells x 50,000 = 7,500 + 750,000 = 757,500 | stated in Abstract | `tab:fulldata`'s 30 `Success/$n$` denominators sum to the same total | n/a | MATCH |

## Overhead decomposition cross-check (independent of the pilot data)

Every overhead figure above was additionally verified against
`Table~tab:environment`'s independently measured primitive sizes (not
derived from `pilot_summary.csv` at all, but from `liboqs`'s own reported
metadata at call time):

- B1 = 96B = X25519 pk (32B) + Ed25519 sig (64B)
- B2 = 5,581B = ML-KEM pk+ct (1184+1088=2,272B) + ML-DSA sig (3,309B)
- B3 = 3,309B = ML-DSA sig only
- B4 = 5,581B = identical to B2 (same PQC component)
- B5 = 8,890B = ML-KEM pk+ct (2,272B) + 2 x ML-DSA sig (2 x 3,309 = 6,618B)

All five decompose exactly with zero residual, confirming the pilot's
measured overhead and the environment table's independently measured
primitive sizes are mutually consistent, not two disconnected numbers
that happen to look similar.

## Discrepancies found

**One**, already identified and corrected in Phase 4
(`research/phase4_data_discrepancy_audit.md`): the payload-encryption-cost
range. No new discrepancy was found in this pass — every value re-checked
against the freshly-regenerated, pixel-verified figures matches the table
and prose values exactly.

## Status: PASS

Every reported number in the manuscript's Results section traces to an
actual row in `results/processed/pilot_summary.csv`, itself traceable to
the 150 raw JSON-lines files under `results/raw/pilot/`. No manuscript
value, table value, or figure value was found inconsistent with its
source data in this pass.
