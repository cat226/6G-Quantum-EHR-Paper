# Notes

Free-form working notes for this project. Not part of the manuscript.
Use this file for scratch thoughts, meeting notes, terminology
decisions, and reminders that don't yet belong in a structured file.

---

## Setup notes (from workspace initialization)

- Workspace created on: (see environment status in setup summary)
- IEEEtran.cls was not found on this system at setup time. It is part
  of the `texlive-publishers` apt package, which was NOT installed
  automatically (per instruction to avoid installing large dependencies
  without confirmation).
- Python packages numpy, pandas, matplotlib, scipy, and scikit-learn
  were found in the system Python, but the project's own `.venv/` was
  created clean (no packages installed into it yet) — install via
  `requirements.txt` after review.
- Qiskit was not found anywhere; needed for QKD protocol simulation.

## Terminology to pin down later
- TODO: precise definition of "hybrid quantum-secure" as used in this
  paper (QKD + PQC combined? PQC only with QKD as future work? etc.)
- TODO: what counts as "6G-enabled" for simulation purposes, given 6G
  standards are not finalized — need to state assumed 6G characteristics
  explicitly (e.g., latency, spectrum, network slicing assumptions).

## Open questions
- TODO: add as they come up.
