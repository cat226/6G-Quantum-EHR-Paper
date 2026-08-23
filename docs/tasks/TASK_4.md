# TASK 4 — QKD Protocol Abstraction and Key-Generation Layer

## 1. Objective

Implement the first research-facing Quantum Key Distribution (QKD)
protocol layer for the 6G-Quantum-EHR-Paper repository.

The purpose of this task is to establish a clean, deterministic,
testable software abstraction for QKD key generation that can later
support BB84 and additional QKD protocol models.

This task implements a software simulation model only. It does not
represent physical quantum hardware or a production QKD deployment.

---

## 2. Scope

Task 4 includes:

- QKD protocol abstraction/interface
- Simplified BB84 protocol model
- Structured QKD key-generation result
- Configurable channel-error model
- QBER calculation
- Sifted-key generation
- Deterministic random-seed support
- Unit tests
- QKD-specific documentation

Task 4 does not include:

- Real quantum hardware
- Hardware-dependent QKD
- Production cryptography
- Post-quantum cryptography (PQC)
- Hybrid QKD-PQC integration
- EHR encryption
- 6G network simulation
- IoMT simulation
- Performance benchmarking
- Scientific experiments
- Experimental results
- Real-world security claims
- Physical quantum-channel simulation

---

## 3. Architectural Position

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

## 4. BB84 Abstraction

The `BB84Protocol` provides a simplified software model of the BB84 QKD protocol. It is NOT a physically accurate quantum simulator. It models the protocol logic probabilistically using pseudo-random numbers to support deterministic testing and high-level evaluation.

## 5. Assumptions

- Alice and Bob generate perfectly random bits and bases.
- The channel introduces bit flips probabilistically according to a configured `channel_error_rate`.
- Error affects only the sifted bits for simplicity.
- The implementation serves computational research, and all parameters are simulation configuration values.

## 6. Simplified Channel Model

The error model probabilistically flips bits in the sifted key based on the `channel_error_rate`. This is a classical software abstraction and NOT a physical quantum-channel model.

## 7. QBER Definition

QBER (Quantum Bit Error Rate) is defined as:
`QBER = number_of_errors / number_of_sifted_bits`
The case of zero sifted bits is explicitly handled to yield `QBER = 0.0` rather than raising a divide-by-zero error.

## 8. Deterministic Execution

The BB84 model relies on Python's built-in `random.Random`, initialized with a `random_seed`. For a fixed `number_of_bits`, `channel_error_rate`, and `random_seed`, the model yields reproducible sifted lengths, QBER values, and final key outputs.

## 9. Limitations and Excluded Functionality

- No privacy amplification or classical error correction is implemented in this task. Final key length simply matches sifted key length.
- Does not store actual secret keys persistently.
- Excludes real quantum hardware, physical security claims, empirical findings, and performance benchmarking.
- No production cryptography or post-quantum integration.

## 10. Validation Strategy

The validation strategy employs deterministic tests via `pytest`:
- Object instantiation and interface checks.
- Verification of structured result fields.
- Ensuring identical seeds produce identical results, and different seeds yield variations.
- Bound checking for QBER (`0.0 <= QBER <= 1.0`).
- Bound checking for lengths (sifted key <= initial bits, final key <= sifted key).
- Rejecting invalid edge cases (e.g., negative bits, out-of-bounds error rates).
- Mock protocol implementations to verify interface generality.

## 11. Relationship to Future Tasks 5+

The QKD protocol abstraction serves as the foundation for experimental network evaluation. Future tasks (Tasks 5+) will interface with the `generate_key()` abstraction without requiring modifications to internal quantum models. This decoupling will allow integrating simulated EHR transmission latency models or evaluating different protocol extensions without perturbing this base QKD layer.
