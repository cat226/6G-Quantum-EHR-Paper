# Environment Manifest

The exact environment in which the Task 8 implementation was validated
(Task 8.5). Recorded so the validation result is reproducible rather than
merely asserted.

This manifest is a **static record of the validated environment**. It
complements, and does not replace, the per-run `environment.json` that
`experiments/run_pilot.py` writes next to each run's raw results
(config path, seed, Python version, platform, timestamp,
liboqs-python version). The per-run file captures *when a run happened*;
this file captures *what the software stack was*.

No usernames, credentials, tokens, or absolute machine paths are recorded
here by design.

---

## 1. Platform

| Item | Value |
|---|---|
| Operating system | Ubuntu 24.04.4 LTS |
| Kernel / platform string | `Linux-6.18.44-fc-v21-x86_64-with-glibc2.39` |
| Architecture | `x86_64` |
| C compiler | GCC 13.3.0 |
| CMake | 3.28.3 |
| Ninja | 1.11.1 |

## 2. Python

| Item | Value |
|---|---|
| Python | **3.12.3** |
| Environment | virtualenv at `.venv/` (git-ignored) |

**Python 3.12 is required, not merely preferred.** `pyproject.toml`
declares `requires-python = ">=3.11"`, but `requirements.txt` pins
`numpy>=2.5`, and numpy 2.5 requires Python >= 3.12. On Python 3.11 the
dependency set is unresolvable. Task 8 was originally validated on
Python 3.12.3, which is what this environment uses.

## 3. Python dependencies

Resolved versions, all satisfying `requirements.txt`:

| Package | Version | `requirements.txt` constraint |
|---|---|---|
| simpy | 4.1.2 | `>=4.1` |
| networkx | 3.6.1 | `>=3.6` |
| numpy | 2.5.2 | `>=2.5` |
| pandas | 3.0.5 | `>=3.0` |
| PyYAML | 6.0.3 | `>=6.0` |
| cryptography | 50.0.0 | `>=44.0` |
| liboqs-python | 0.16.0 | `>=0.16` |
| pytest | 9.1.1 | `>=9.0` (dev) |

Transitive: `cffi 2.1.1`, `pycparser 3.0`, `python-dateutil 2.9.0.post0`,
`six 1.17.0`, `packaging 26.3`, `pluggy 1.6.0`, `iniconfig 2.3.0`,
`Pygments 2.21.0`.

The full resolved set is pinned in **`requirements.lock.txt`**.
`requirements.txt` remains the Task 8 dependency *specification* (lower
bounds, with per-package justification); the lockfile is the resolved
*record* for reproducing this validated run.

Note: `numpy`, `pandas`, and `networkx` are declared dependencies but are
not imported by any module in `src/`, `tests/`, or `experiments/`.
`networkx` is documented as scaffolding for a possible multi-site
extension. They are installed for spec fidelity, not because the pilot
needs them.

## 4. liboqs (the C library)

**`liboqs` is not a pip package** — the Python wrapper binds to a C
library that must be built separately.

| Item | Value |
|---|---|
| Source | https://github.com/open-quantum-safe/liboqs |
| **Commit** | `8979276ad1eb008215aa78a3c56b3649f604bbb1` |
| Commit date | 2026-08-19 |
| Library version | **0.16.0** (`liboqs.so.0.16.0`, soname `liboqs.so.9`) |
| Build type | Release, shared library |
| Installed to | `/usr/local/lib`, registered via `ldconfig` |

Built as a **minimal build enabling only the two algorithms this project
uses** — a full build compiles every algorithm in liboqs, which costs
significant build time for no benefit here:

```bash
git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -GNinja -DCMAKE_BUILD_TYPE=Release \
  -DOQS_MINIMAL_BUILD="KEM_ml_kem_768;SIG_ml_dsa_65" \
  -DOQS_BUILD_ONLY_LIB=ON -DBUILD_SHARED_LIBS=ON ..
ninja
sudo cp -P lib/liboqs.so* /usr/local/lib/ && sudo ldconfig
```

OS-level prerequisites: `build-essential`, `cmake`, `ninja-build`,
`libssl-dev`.

**Pin the commit above when reproducing.** `--depth 1` clones the moving
`main` branch; without the commit the build is not reproducible.

### Enabled algorithms (verified, not assumed)

```
enabled KEMs: ('ML-KEM-768',)
enabled SIGs: ('ML-DSA-65', 'ML-DSA-65-extmu')
```

Only the required algorithms are compiled in. `src/crypto/pqc.py` raises
at import if either is absent, so a build missing them fails loudly
rather than silently substituting a different algorithm.

### Parameter sizes reported by this build

| Algorithm | Field | Bytes |
|---|---|---|
| ML-KEM-768 | public key | 1184 |
| ML-KEM-768 | ciphertext | 1088 |
| ML-KEM-768 | shared secret | 32 |
| ML-KEM-768 | secret key | 2400 |
| ML-DSA-65 | public key | 1952 |
| ML-DSA-65 | signature | 3309 |
| ML-DSA-65 | secret key | 4032 |

These match the values recorded in `docs/implementation_notes.md`
Part II §3 exactly — an independent cross-check that this rebuilt
environment is equivalent to the original Task 8 environment.

## 5. Reproducing this environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt      # or requirements.txt for the spec
# then build liboqs at the pinned commit above
pytest tests/ -v
python experiments/validate_phase17.py
```

## 6. Validation status in this environment

| Gate | Result |
|---|---|
| `pytest tests/` | **60 passed**, 0 failed, 0 skipped, 0 errors |
| `experiments/validate_phase17.py` | **8/8 checks PASS** |
| Cryptographic construction | Verified byte-identical to an independent HKDF reference |
| B4/B5 divergence | Verified across all four QKD availability scenarios |
| Determinism under fixed seed | Verified, with the bounded-wait path active |

The 60 tests are the original Task 8 suite of 50, plus 10 added in
Task 8.5 covering the adaptive bounded-wait path
(`tests/test_b5_wait_path.py`).

**The pilot has not been run.** This manifest records a validated
environment, not an experiment.
