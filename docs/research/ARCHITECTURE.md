# Research Architecture

## 1. Research Scope
This repository supports the computational evaluation of quantum-secure EHR communication in a future 6G-oriented network context. The work focuses on modeling and analysis rather than production deployment. Note that 6G standards are not finalized, and this project serves as a forward-looking research context. Additionally, we make no claims of novelty regarding the integration of 6G, QKD, PQC, and EHR.

## 2. Repository Architecture
The repository is structured to maintain a clear separation of concerns:
- `src/`: Core logic, protocols, and simulation code.
- `tests/`: Unit tests and integration checks to ensure implementation correctness.
- `experiments/`: Drivers and scripts to run structured, reproducible experiments.
- `config/`: Configuration files and parameters for simulations and protocols.
- `results/`: Output directories for generated data and plots.
- `docs/`: Project documentation, research notes, and task specifications.

## 3. Source Module Responsibilities
- `src/crypto/`: Cryptographic primitives and cryptographic protocol components used by later experimental tasks.
- `src/qkd/`: Quantum Key Distribution (QKD) models and simulated properties.
- `src/protocols/`: Security and communication protocol configurations evaluated by later experimental tasks.
- `src/simulation/`: Network and latency modeling for the 6G-oriented context.
- `src/metrics/`: Evaluation metrics and measurement calculations.

## 4. Protocol vs Simulation Separation
To ensure rigor and modularity, protocol and security logic remain strictly separated from network and simulation mechanics. Protocols do not assume specific network topologies, and simulations can test varying protocol configurations independently.

## 5. Experiment Separation
Experiment drivers belong exclusively under the `experiments/` directory. They act as orchestrators that consume explicitly defined configurations from `config/` and execute modules from `src/` to produce results.

## 6. Results Organization
The results are organized to distinguish raw data from derived artifacts:
- `results/raw/`: Original, unmodified output data from experiments.
- `results/processed/`: Derived data, aggregations, and transformed results.
- `results/figures/`: Generated plots, charts, and visualizations for analysis.
Raw data must remain distinguishable from derived/processed data and figures.

## 7. Reproducibility Principles
This research adheres to strict reproducibility principles:
- **Configuration-driven experiments**: All parameters are defined externally, avoiding hardcoded values.
- **Deterministic seeds**: Used wherever applicable to ensure repeatable runs.
- **Explicit dependency management**: Handled systematically (e.g., via `requirements.txt`).
- **Separation of source code and generated results**: Clear boundaries between code and outputs.
- **Recording experimental parameters**: Automatically logged with results.
- **Avoiding undocumented manual changes**: All configuration changes must be tracked.

## 8. Current Task 0 Boundary
This task focuses exclusively on initializing the repository and experimental architecture. Task 0 does not implement:
- cryptography
- QKD
- EHR transmission
- protocols
- simulation
- metrics
- experiments
- statistical analysis

## 9. QKD Integration Boundary

The QKD layer is intentionally separated from future network,
application, and EHR layers.

The intended architecture is:

```text
6G / Network Context
        |
        v
Future Network Simulation
        |
        v
QKD Protocol Abstraction
        |
        v
BB84 Software Model
        |
        v
Key-Generation Metrics
```

## 10. PQC Integration Boundary

The PQC layer is intentionally separated from the QKD layer, future network, application, and EHR layers.
It represents an independent, classical baseline using standardized Post-Quantum Cryptography (ML-KEM) running over standard classical channels.

The intended architecture is:

```text
6G / Network Context
        |
        v
Future Network Simulation
        |
        v
PQC Protocol Abstraction
        |
        v
ML-KEM Software Adapter
        |
        v
Key-Establishment Metrics
```

## 11. Hybrid QKD-PQC Integration Boundary

The hybrid layer combines the independently established QKD and PQC secrets using a deterministic HKDF-SHA256 combiner.

```text
QKD ───────────┐
               |
               +──> Hybrid Combiner ──> K_HYBRID
               |
ML-KEM ────────┘
```
