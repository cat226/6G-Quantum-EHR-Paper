# TASK 5 — Post-Quantum Cryptography Baseline and Key-Establishment Layer

## 1. Objective

Implement the post-quantum cryptography (PQC) baseline required for the
later hybrid QKD-PQC evaluation.

The purpose of this task is to establish a clean, testable PQC
key-establishment abstraction that can later be evaluated alongside
the QKD model from Task 4.

Task 5 is a baseline implementation task.

It must NOT claim that combining QKD and PQC is itself novel.

The later research contribution concerns the evaluation and
characterization of adaptive QKD-PQC operation for EHR workloads under
varying QKD availability.

---

## 2. Scope

Task 5 includes:

- PQC key-establishment abstraction
- ML-KEM-based key establishment
- structured PQC result model
- deterministic testability where supported
- explicit algorithm/configuration identification
- encapsulation/decapsulation validation
- unit tests
- documentation
- integration boundary for later hybrid evaluation

Task 5 does NOT include:

- QKD-PQC hybrid orchestration
- adaptive switching
- 6G network simulation
- EHR workload simulation
- performance benchmarking
- experimental evaluation
- security claims beyond the selected standardized algorithm
- invention/patent claims
- fabricated performance parameters

---

## 3. Relationship to Task 4

Task 4 established:

```text
QKD Protocol Abstraction
        |
        v
BB84 Software Model
```

Task 5 establishes the parallel PQC branch:

```text
PQC Protocol Abstraction
        |
        v
ML-KEM Software Adapter
```

Task 6 will later introduce the hybrid coordination layer above these two independent abstractions.

---

## 4. Implementation Details

### Dependency
The `cryptography>=50.0.0` library was introduced as the cryptographic primitive provider to access the standardized `mlkem` API. The exact version tested is `cryptography 50.0.0`.

### Selected Algorithm
- **Algorithm**: ML-KEM
- **Parameter Set**: ML-KEM-768 (Default) and ML-KEM-1024

### Cryptographic Baseline
The `MLKEMProtocol` provides:
- **Key Generation**: Uses the underlying C/Rust cryptography bindings (`MLKEM768PrivateKey.generate()`). The exact private-key representation used is the FIPS 203 64-byte raw seed material (`d || z`), exposed via `private_bytes_raw()`.
- **Encapsulation Return Contract**: The `encapsulate()` method returns a tuple in the exact order `(shared_secret, ciphertext)`, where `shared_secret` is 32 bytes and `ciphertext` is 1088 bytes (for ML-KEM-768).
- **Decapsulation Behavior**: Expects the 1088-byte ciphertext and the 64-byte raw seed. The private key is reconstructed using `.from_seed_bytes()`.
- **Error/Implicit-Rejection Behavior**: Validates lengths prior to execution. For malformed ciphertext sizes, decapsulation raises a `ValueError`. For mutated ciphertext of the correct size, FIPS 203 implicit rejection semantics are observed: the library returns a deterministically generated pseudo-random shared secret that does not match the original secret, without raising an exception.
- **Structured Result Metadata**: The `PQCResult` dataclass records the properties (lengths, algorithm name) without persisting actual secret materials.

### Security Boundary
Secret keys and shared secrets are passed ephemerally. The result object intentionally omits the key materials.

---

## 5. Limitations
This is a baseline configuration setup for future integration.
- This task does not execute a real key exchange over a network.
- It does not combine the shared secret with QKD (reserved for Task 6).
