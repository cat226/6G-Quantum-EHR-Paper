# TASK 6 — Hybrid QKD + ML-KEM Key Establishment Layer

## 1. Objective

Task 6 establishes the baseline hybrid key-establishment mechanism
for the 6G-Quantum-EHR-Paper research repository.

The hybrid layer combines two independently implemented
key-establishment mechanisms:

1. Quantum Key Distribution (QKD), based on the BB84 software
   abstraction established in Task 4.
2. ML-KEM, established as the post-quantum cryptography baseline in
   Task 5.

The objective is to derive a single hybrid symmetric key from both
independently established secrets.

The baseline architecture is:

```text
                    Key Establishment Request
                             |
                +------------+------------+
                |                         |
                v                         v
          +-----------+             +-----------+
          |    QKD    |             |  ML-KEM   |
          |   BB84    |             |    KEM    |
          +-----+-----+             +-----+-----+
                |                         |
              K_QKD                     K_PQC
                |                         |
                +------------+------------+
                             |
                             v
                    +------------------+
                    | Hybrid Combiner  |
                    |   HKDF-SHA256    |
                    +--------+---------+
                             |
                             v
                        K_HYBRID
```

## 2. Hybrid Combiner Design

### 2.1 Cryptographic Construction
The hybrid combiner utilizes **HKDF-SHA256** (HMAC-based Extract-and-Expand Key Derivation Function) from the standard cryptography library to derive the final key.
Both `K_QKD` and `K_PQC` are mandatory. The final key `K_HYBRID` is derived as:
`K_HYBRID = HKDF-SHA256(canonical_encode(K_QKD, K_PQC), info=context, length=32)`

### 2.2 Canonical Encoding
To avoid ambiguity (e.g. distinguishing K_QKD="A", K_PQC="BC" from K_QKD="AB", K_PQC="C"), a length-delimited canonical encoding is used:
`encoded = [4-byte length of K_QKD] || [K_QKD] || [4-byte length of K_PQC] || [K_PQC]`
This explicitly separates and identifies both constituent components.

### 2.3 Domain Separation
The derivation uses an explicit context string to separate it from other derivations.
`context = "6G-Quantum-EHR-Paper/hybrid-key-establishment/v1"`

### 2.4 Salt Behavior
HKDF allows for an optional salt. In this baseline, `salt=None` is used explicitly. The rationale is that `K_QKD` and `K_PQC` themselves provide the required entropy and cryptographic uniqueness for the baseline combination; an additional randomized salt is unnecessary for this deterministic task.

### 2.5 Failure Semantics
This task provides a fixed baseline. Both mechanisms are strictly required.
- If QKD fails, the hybrid establishment fails.
- If ML-KEM fails, the hybrid establishment fails.
No adaptive switching, QBER thresholds, or fallback logic are included.

## 3. Public API
The hybrid layer exposes two clean interfaces:
- `combine(k_qkd: bytes, k_pqc: bytes) -> bytes`: A raw cryptographic combiner.
- `establish_hybrid_key(k_qkd: bytes, k_pqc: bytes) -> Tuple[bytes, HybridResult]`: A higher-level orchestration returning the key and metadata separately.

## 4. Limitations and Future Work
- Does not contain adaptive switching or QBER threshold-based fallbacks. Adaptive logic is reserved for future tasks.
- No EHR payloads, network simulation (6G latency), or hardware experiments are implemented here.
