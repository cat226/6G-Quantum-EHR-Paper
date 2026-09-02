# Reproducibility

The complete, ordered command sequence to go from a clean checkout of this
repository to the compiled manuscript PDF, reproducing every number and
figure in `paper/manuscript/main.pdf` from scratch. Every command below is
taken directly from this repository's own scripts and configuration files,
not invented for this document — see the cross-reference at the end of
each section.

## 1. Environment setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Python 3.12 is required: `requirements.txt` pins `numpy>=2.5`, which needs
Python >= 3.12.

## 2. Dependency installation

```bash
pip install -r requirements.lock.txt   # exact validated versions
```

`liboqs` (the C library providing ML-KEM-768 and ML-DSA-65) is **not**
installed via pip and requires a separate build:

```bash
sudo apt install cmake ninja-build build-essential libssl-dev
git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -GNinja -DCMAKE_BUILD_TYPE=Release \
  -DOQS_MINIMAL_BUILD="KEM_ml_kem_768;SIG_ml_dsa_65" \
  -DOQS_BUILD_ONLY_LIB=ON -DBUILD_SHARED_LIBS=ON ..
ninja
sudo cp build/lib/liboqs.so* /usr/local/lib/
sudo ldconfig
cd ../..
```

This builds only the two algorithms this project uses (`OQS_MINIMAL_BUILD`)
rather than every algorithm liboqs supports, which is unnecessarily slow
for this project's scope. The exact commit and measured primitive sizes
used for the manuscript's own results are recorded in
`docs/environment_manifest.md` and `paper/manuscript/main.tex`'s
Table `tab:environment` — a different liboqs commit or build flag set may
change PQC operation timings and could, in principle, change measured
latency numbers, though not the qualitative behavior this paper reports.

Source: `requirements.txt`, `docs/implementation_notes.md` (liboqs build
steps, Part II §1).

## 3. Dataset acquisition

Not applicable. This project uses no external dataset. The EHR transaction
workload is entirely synthetic and procedurally generated at simulation
time (`src/workload/`), not downloaded, licensed, or drawn from any real
clinical source.

## 4. Dataset preprocessing

Not applicable, for the same reason as above — there is no external
dataset to preprocess. The workload generator's parameters (payload
classes, transaction mix) are set via the experiment configuration file
(`config/pilot.yaml`), not preprocessed from raw input data.

## 5. Workload generation

Workload generation happens inline during simulation execution (Step 6
below); there is no separate workload-generation command. The generator
lives in `src/workload/` and is invoked by the simulation harness
(`src/simulation/`) per transaction, seeded from the same top-level seed
as every other stochastic component (see `src/utils/random.py`'s
`SeedManager`).

## 6. Experiment execution

Run the test suite first, to confirm the environment is correctly set up
before spending time on the full pilot:

```bash
pytest tests/ -v          # expect 61 passed
python experiments/validate_phase17.py   # expect 8/8
```

Run a single pilot cell (fast, for a quick sanity check):

```bash
python experiments/run_pilot.py \
    --config config/pilot.yaml \
    --seed 42 \
    --output results/raw/pilot \
    --baseline B5 \
    --qkd-availability 0.5 \
    --device-count 10
```

Run the complete 30-configuration pilot (5 baselines x 3 QKD availability
levels x 2 device counts, 5 repetitions each — this is what produced the
results reported in the manuscript):

```bash
python experiments/run_pilot.py \
    --config config/pilot.yaml \
    --seed 42 \
    --output results/raw/pilot \
    --full-pilot
```

This writes 150 raw JSON-lines files to `results/raw/pilot/` (one per
baseline/availability/device-count/repetition combination), each
alongside an `environment.json` recording the config path, seed, Python
version, platform, and timestamp used to produce it. Every descriptive
statistic reported anywhere in the manuscript is computed from these raw,
per-transaction records — never from a pre-aggregated value — per the
metrics discipline in `src/metrics/collector.py`.

Determinism: re-running the identical command with the identical seed and
config reproduces every deterministic field (transaction identifiers,
payload sizes, selected mode, controller state, success outcome, and
simulated timestamp) exactly, independently verified during this
project's own validation (see `paper/manuscript/main.tex`, Appendix
"Reproducibility").

Source: `experiments/run_pilot.py`, `config/pilot.yaml`.

## 7. Statistical analysis

```bash
python experiments/analyze_pilot.py \
    --input results/raw/pilot \
    --output results/processed/pilot_summary.csv
```

This aggregates the 150 raw files into one 30-row CSV (`pilot_summary.csv`,
one row per baseline/availability/device-count cell, pooled across the 5
repetitions), computing means, medians, 95th percentiles, and bootstrap
95% confidence intervals per cell — the exact numbers reported in the
manuscript's Results section, Table `tab:summary`, and Table
`tab:fulldata`.

Source: `experiments/analyze_pilot.py`, `src/metrics/aggregator.py`.

## 8. Figure generation

```bash
python experiments/generate_figures.py \
    --input results/processed/pilot_summary.csv \
    --output paper/figures
```

Regenerates all three results figures (`fig1_success_rate_vs_qkd_availability`,
`fig2_b5_latency_vs_qkd_availability`, `fig3_overhead_by_baseline`) as
both PDF (used in the compiled manuscript) and PNG, directly from the
processed CSV — no manual editing of plotted values occurs anywhere in
this pipeline. The other three figures in the manuscript (the system
architecture diagram, the message sequence diagram, and the adaptive
decision flowchart) are native TikZ, defined directly in
`paper/manuscript/main.tex` and requiring no separate generation step —
they compile as part of Step 9.

Source: `experiments/generate_figures.py`.

## 9. Manuscript compilation

```bash
cd paper/manuscript
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Four passes are required: the first pass writes citation keys and labels
that `bibtex` needs, `bibtex` resolves the bibliography against
`../references/references.bib`, and two further `pdflatex` passes resolve
the resulting citation numbers and cross-references (LaTeX's own
two-pass-minimum convention for a document with both a bibliography and
internal `\ref`/`\label` cross-references). The result,
`paper/manuscript/main.pdf`, should compile with zero fatal errors, zero
undefined citations, and zero undefined references — verified in this
audit pass (37 pages).

## Full pipeline, start to finish

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt
# (build and install liboqs -- see Section 2 above)
pytest tests/ -v
python experiments/run_pilot.py --config config/pilot.yaml --seed 42 \
    --output results/raw/pilot --full-pilot
python experiments/analyze_pilot.py --input results/raw/pilot \
    --output results/processed/pilot_summary.csv
python experiments/generate_figures.py --input results/processed/pilot_summary.csv \
    --output paper/figures
cd paper/manuscript
pdflatex -interaction=nonstopmode main.tex && bibtex main && \
    pdflatex -interaction=nonstopmode main.tex && \
    pdflatex -interaction=nonstopmode main.tex
```
