# Development Environment

## 1. Supported Python Version
The project establishes Python 3.12.10 as the supported baseline development version.

## 2. Environment Creation
It is recommended to use an isolated virtual environment.

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Unix-like Systems:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Dependency Installation
Install the minimal dependencies required for the current baseline:
```bash
pip install -r requirements.txt
```

## 4. Running Tests
Tests are executed using `pytest`. From the project root, run:
```bash
pytest
```

## 5. Running Experiments
No experiments exist yet. In the future, experiments will be executed via orchestrator scripts placed in the `experiments/` directory, consuming configurations from `config/`.

## 6. Reproducibility
To ensure reproducibility, future tasks must adhere to:
- **Dependency versions**: Explicitly constrained in `requirements.txt`. Exact environment versions should be captured for reproducible experimental runs.
- **Configuration files**: Managed explicitly in `config/` (e.g., `default.yaml`).
- **Random seeds**: Explicitly declared and recorded. No uncontrolled global randomness.
- **Experiment parameters**: Recorded alongside results.
- **Environment information**: Captured via `src/environment.py`.
- **Result provenance**: Clear separation of `results/raw/` and `results/processed/`.

## 7. Environment Verification
A contributor can verify their environment by running the test suite (`pytest`) and checking the output of `src/environment.py` to ensure Python versions and platform details align with project requirements.

## Task 5 Dependency Updates
- cryptography>=50.0.0: Required for standard ML-KEM implementation.
