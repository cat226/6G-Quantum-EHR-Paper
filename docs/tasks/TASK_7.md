# TASK 7 — Cryptographic Construction and Simulation Parameter Validation

**Project:** Latency-Aware Adaptive QKD-PQC Key Establishment for Electronic Health Record Sharing in 6G-Edge Healthcare Networks

**Depends on:** Task 6 — approved

**Status:** Validation and specification only. No implementation, experiments, or fabricated numerical results.

---

## 1. Objective

Validate and freeze the cryptographic construction and simulation parameters required for Task 8.

Task 7 must resolve:

1. the hybrid QKD + ML-KEM key-combination construction;
2. the selected cryptographic primitives;
3. QKD simulation parameters and their evidence status;
4. synthetic EHR workload parameters;
5. 6G-edge simulation abstractions;
6. baseline fairness;
7. the reduced pilot experiment;
8. the statistical analysis plan;
9. the exact implementation structure for Task 8.

Task 7 must NOT implement the simulation framework.

---

## 2. Research Architecture

The five baselines remain:

- **B1 — Classical**
- **B2 — PQC-only**
- **B3 — QKD-only**
- **B4 — Static Hybrid**
- **B5 — Adaptive Hybrid — Proposed**

B5 is the proposed contribution.

B4 exists as a control baseline to isolate the value of adaptivity.

Do not reframe the research as mandatory hybrid operation.

The central research question remains whether adaptive QKD-PQC key establishment provides useful latency, reliability, and key-management behavior under changing QKD availability.

---

## 3. Evidence Labels

Every parameter or literature-dependent claim must use one of:

### ESTABLISHED

Confirmed through the project's verified literature corpus or authoritative standards.

### DESIGN ASSUMPTION

Supported by a source found during research but not fully verified.

### RECALLED-UNVERIFIED

Based on model knowledge or recalled literature and requiring verification before manuscript citation.

### MODELED ASSUMPTION

A simulation choice rather than a measured real-world fact.

### SENSITIVITY VARIABLE

A modeled parameter whose value materially affects results and therefore requires sensitivity analysis.

### EXPERIMENTAL DESIGN CHOICE

A parameter chosen by this project, such as pilot availability levels.

Never silently convert an assumption into a fact.

---

# PART 1 — Hybrid Key Construction

## 4. Required Construction

Replace Task 6's unspecified KDF construction with the explicit HKDF construction:

IKM = QKD_key_material || ML-KEM_shared_secret

PRK = HKDF-Extract(
    salt=session_salt,
    IKM=IKM
)

session_key = HKDF-Expand(
    PRK,
    info=context_binding_label,
    L=key_length
)

Use:

- HKDF;
- SHA-256;
- explicit `salt`;
- explicit `info`;
- explicit output length.

The context/domain-separation value MUST NOT be concatenated directly into the secret IKM.

The context belongs in the KDF context mechanism (`info`).

---

## 5. Security Claim Boundary

The implementation may use the HKDF construction as an engineering-level key combiner.

However, the paper MUST NOT claim that the specific QKD + ML-KEM construction has a formal "at least one component remains secure" proof unless that exact claim has been verified for this construction.

The general hybrid-KEM combiner literature may support the two-input KEM case, but QKD key material is not itself a KEM output.

Therefore:

**Allowed claim:**

> An engineering-level HKDF-based combination of independently generated QKD and ML-KEM secret material.

**Not allowed without additional verification:**

> The specific QKD+ML-KEM construction formally guarantees security whenever either component remains secure.

This distinction must remain visible in the documentation and implementation notes.

---

## 6. Required Authentication

The classical control channel must be authenticated.

Use:

- ML-DSA-65 for B2–B5;
- Ed25519 for B1.

For B3, "QKD-only" refers to the session-key material source, not the absence of classical authentication.

Do not claim that ML-DSA authenticates the physical quantum channel itself.

---

# PART 2 — Cryptographic Primitive Selection

## 7. Fixed Primitive Set

Use one fixed parameter set for the main study.

### B1

- X25519
- Ed25519
- AES-256-GCM

### B2

- ML-KEM-768
- ML-DSA-65
- AES-256-GCM

### B3

- QKD-derived symmetric material
- ML-DSA-65
- AES-256-GCM

### B4

- QKD material
- ML-KEM-768
- ML-DSA-65
- HKDF
- AES-256-GCM

### B5

Adaptive selection between:

- B2 path; or
- B4 path.

Use the same AES-256-GCM payload encryption across all baselines.

Do not perform an algorithm comparison in Task 7.

---

# PART 3 — QKD Model

## 8. QKD Evidence

The project may use verified field-deployment information only as a plausibility anchor.

Do not claim one QKD deployment represents QKD generally.

The following remain modeled:

- QKD generation rate;
- QKD pool capacity;
- outage pattern;
- availability;
- QKD consumption behavior.

Generation rate MUST be treated as a sensitivity variable until a defensible literature range is established.

---

## 9. QKD Pool

The simulation will later implement:

```text
QKDPool(
    level,
    capacity,
    generation_rate
)
```

These must be tracked as explicit state variables during the simulation.

---

## 10. QKD Availability

The pilot will evaluate these QKD availability scenarios:

- **100%**
- **50%**
- **0%**

These are **EXPERIMENTAL DESIGN CHOICES**, intended to force the adaptive behavior into specific branches. They are NOT claims that real QKD networks naturally operate exactly at these availability percentages.

If a full study is later justified, candidate availability levels are 100%, 75%, 50%, 25%, and 0%. Task 7 must NOT execute that study.

---

# PART 4 — Synthetic EHR Workload

## 11. Workload Parameters

The simulation must use **synthetic EHR-inspired data only**. No real patient data, identifiers, or histories will be used.

Payload classes (labeled as **MODELED ASSUMPTION** unless verified):

- **Small:** approximately 1–5 KB
- **Medium:** approximately 20–80 KB
- **Large:** approximately 200 KB–1 MB

These are simulation categories, not measured EHR distributions.

Transaction types:

- **read**
- **write**
- **share**

The **share** transaction receives primary emphasis as this project models secure EHR sharing.

Transaction criticality:

- **routine**
- **emergency**

Criticality is NOT an independent pilot axis. The pilot experiment will use **MEDIUM** payloads only.

---

# PART 5 — 6G-Edge Model

## 12. Simulation Abstraction

The future simulation conceptually represents:

```text
EHR client / IoMT
        |
6G access abstraction
        |
edge gateway
        |
hospital network
        |
EHR server
```

This is a **SIMULATION ABSTRACTION**, not a finalized 6G protocol stack.

The paper makes no claims regarding finalized 6G PHY, MAC, slicing standards, or real-world 6G/hospital measurements.

The network model supports abstraction of:

- network latency
- throughput
- packet loss
- network load
- edge processing delay
- device population

For the pilot, network load will be **NOMINAL** only.

---

# PART 6 — Baseline Fairness

## 13. Fairness Definition

All five baselines must share identical:

- synthetic EHR workload
- transaction schedule
- network model
- AES-256-GCM encryption
- measurement system
- result schema

Only the cryptographic and key-management behaviors differ.

The failure behaviors are frozen as follows:

- **B3 (QKD-only):** Fails/blocks when QKD is unavailable.
- **B4 (Static Hybrid):** Fails/blocks when QKD is unavailable. **NO FALLBACK.**
- **B5 (Adaptive Hybrid):** Selects B2 (PQC-only) when QKD is unavailable.

---

# PART 7 — Pilot Design

## 14. Pilot Matrix

The pilot matrix is frozen as:

- **QKD availability:** 100%, 50%, 0%
- **Device/user count:** 10, 1000
- **Payload:** medium only
- **Network load:** nominal only
- **Baselines:** B1, B2, B3, B4, B5

Maximum configured cells = 3 × 2 × 1 × 1 × 5 = **30 cells**.

A provisional repetition count of **5 repetitions** per configuration will be used to estimate variance and runtime. Do not arbitrarily choose a large full-study repetition count now.

## 15. Pilot Purpose

The pilot is intended to:

1. validate the simulation harness;
2. validate all five baselines;
3. estimate variance;
4. check qualitative behavior;
5. expose mode synchronization problems;
6. expose QKD-pool modeling problems;
7. expose fairness violations;
8. estimate runtime.

Task 8 will execute this pilot. Task 7 does not.

## 16. Six Expansion Criteria

The full experiment may proceed only if ALL SIX criteria pass:

1. **Criterion 1:** All 30 pilot configurations complete without unhandled errors.
2. **Criterion 2:** Fairness audit passes.
3. **Criterion 3:** B5 demonstrably switches between PQC and hybrid modes at 50% QKD availability.
4. **Criterion 4:** At 100% QKD availability, B5 behaves comparably to B4. At 0% QKD availability, B5 behaves comparably to B2.
5. **Criterion 5:** Observed pilot variance is sufficiently controlled to distinguish the planned experimental conditions.
6. **Criterion 6:** Pilot runtime is feasible for the remaining project timeline.

If any criterion fails, the project must STOP. Do not fabricate data, manipulate parameters to force a pass, or automatically expand the study.

---

# PART 8 — Statistical Analysis Plan

## 17. Descriptive and Inferential Statistics

Descriptive statistics to record:

- mean
- median
- standard deviation
- 95th percentile

Use **95% bootstrap confidence intervals** for appropriate outcome variables (e.g. skewed latency).

Default non-parametric baseline comparison: **Mann-Whitney U**.

For multiple comparisons, use a correction such as **Bonferroni** or **Benjamini-Hochberg/FDR**.

Do not generate p-values or claim significance before data exists.

---

# PART 9 — Reproducibility and Result Schema

## 18. Reproducibility Requirements

Future Task 8 runs MUST record:

- explicit random seed
- configuration snapshot
- experiment ID
- git commit
- Python version
- dependency versions
- timestamp
- execution environment

The runner must refuse execution without an explicit seed. Same configuration + same seed must reproduce equivalent results.

## 19. Result Schema

Raw results must be emitted as **JSON Lines**.
Aggregated results must be emitted as **CSV**.
Plots must be generated only from the aggregated CSV.

Per-run records must contain:

- experiment ID
- baseline
- seed
- availability
- device count
- payload class
- network load
- transaction ID
- selected mode
- success/failure
- failure reason
- latency
- message bytes
- QKD pool metadata

**NEVER STORE:** private keys, shared secrets, QKD key bytes, ML-KEM shared secrets, derived session keys, or plaintext EHR data.

---

# PART 10 — Task 8 Directory Specification

## 20. Specified Implementation Structure

Task 8 will implement the following structure (do NOT create this yet):

```text
experiments/
  src/
    baselines/
      baseline_interface.py
      b1_classical.py
      b2_pqc_only.py
      b3_qkd_only.py
      b4_static_hybrid.py
      b5_adaptive.py

    qkd_model/
      qkd_pool.py
      qkd_availability.py

    pqc/
      ml_kem.py
      ml_dsa.py

    crypto/
      kdf.py
      aead.py
      classical_baseline.py

    adaptive/
      controller.py
      mode_sync.py

    workload/
      ehr_generator.py
      transaction.py

    network/
      sixg_model.py
      topology.py

    simulation/
      engine.py
      scenario.py

    metrics/
      collector.py
      aggregator.py

    runner/
      experiment_runner.py
      cli.py

  configs/
    pilot/
    full_study/
    parameters.yaml

  results/
    pilot/
      raw/
      aggregated/
    full_study/
      raw/
      aggregated/

  plots/
    pilot/
    full_study/
```

---

# PART 11 — Evidence Discipline and Literature Verification

## 21. Evidence Discipline

Every parameter must explicitly be categorized by one of the evidence labels defined in Section 3. If a source cannot be verified, explicitly mark it as **"VERIFICATION REQUIRED"**.

Do not invent citations, metrics, measurements, DOIs, authors, or deployment statistics.

## 22. Literature Verification Priorities

Where authoritative sources are available, the project verifies against:

- RFC 5869 (HKDF)
- NIST FIPS 203 (ML-KEM)
- NIST FIPS 204 (ML-DSA)
- Relevant hybrid KEM combiner literature

**Primary Open Verification Item:**
What exact literature supports the formal security/composability claim for combining QKD-derived key material (a non-KEM output) with ML-KEM-derived secret material using HKDF? This remains an open limitation.