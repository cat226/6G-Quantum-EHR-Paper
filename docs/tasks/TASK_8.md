# TASK 8 — Simulation Framework, Baseline Implementations, and Pilot Experiment

## Objective

Implement the reproducible simulation framework defined in TASK 7 and execute the approved pilot experiment.

Task 8 has two stages:

1. Implement and validate the simulation framework.
2. Execute the ≤30-cell pilot defined in TASK 7.

The pilot must be completed before any decision is made about a full-scale experiment.

No fabricated, manually entered, or inferred experimental results are permitted.

---

## 1. Locked Research Architecture

The simulation must implement exactly five baselines.

### B1 — Classical

- X25519
- Ed25519
- AES-256-GCM

### B2 — PQC-only

- ML-KEM-768
- ML-DSA-65
- AES-256-GCM

### B3 — QKD-only

- QKD-derived key material
- ML-DSA-65
- AES-256-GCM

B3 must fail/block when QKD material is unavailable.

### B4 — Static Hybrid

- QKD
- ML-KEM-768
- ML-DSA-65
- HKDF-SHA256
- AES-256-GCM

B4 requires BOTH QKD and ML-KEM material.

B4 must NOT fall back to PQC-only operation.

### B5 — Adaptive Hybrid

B5 adaptively selects between:

- B2 PQC-only operation
- B4 hybrid operation

When QKD is available:

B5 → hybrid mode.

When QKD is unavailable:

B5 → PQC-only mode.

B5 must never silently fail solely because QKD is unavailable if ML-KEM is available.

---

## 2. Existing Repository Must Be Preserved

Before implementation, inspect:

docs/tasks/TASK_1.md
docs/tasks/TASK_2.md
docs/tasks/TASK_3.md
docs/tasks/TASK_4.md
docs/tasks/TASK_5.md
docs/tasks/TASK_6.md
docs/tasks/TASK_7.md

docs/research/ARCHITECTURE.md
docs/research/DEVELOPMENT.md

research/evidence/README.md
research/literature_matrix.csv
research/parameter_provenance.csv

Inspect:

src/qkd/
src/pqc/
src/hybrid/
tests/

Do not rewrite previous tasks.

Do not replace Task 4 QKD behavior.

Do not replace Task 5 ML-KEM behavior.

Do not replace Task 6 hybrid derivation.

Reuse existing implementations through adapters/interfaces where possible.

---

# 3. Required Directory Structure

Create:

experiments/

    src/

        baselines/
            __init__.py
            baseline_interface.py
            b1_classical.py
            b2_pqc_only.py
            b3_qkd_only.py
            b4_static_hybrid.py
            b5_adaptive.py

        qkd_model/
            __init__.py
            qkd_pool.py
            qkd_availability.py

        pqc/
            __init__.py
            ml_kem.py
            ml_dsa.py

        crypto/
            __init__.py
            kdf.py
            aead.py
            classical_baseline.py

        adaptive/
            __init__.py
            controller.py
            mode_sync.py

        workload/
            __init__.py
            ehr_generator.py
            transaction.py

        network/
            __init__.py
            sixg_model.py
            topology.py

        simulation/
            __init__.py
            engine.py
            scenario.py

        metrics/
            __init__.py
            collector.py
            aggregator.py

        runner/
            __init__.py
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

Create appropriate __init__.py files.

Do not create fake result files.

---

# 4. Baseline Interface

All baselines must implement a common interface.

The interface should support:

- initialization
- session/key establishment
- encryption
- transaction execution
- failure reporting
- selected mode reporting

The exact Python API should be clean and typed.

Every baseline should return a structured result rather than arbitrary dictionaries scattered throughout the code.

At minimum, the baseline result must support:

- success/failure
- failure reason
- selected mode
- key-establishment status
- encryption status
- timing information

Do NOT return actual secret material in experiment results.

---

# 5. Secret Handling

NEVER write these to result files:

- private keys
- QKD key bytes
- ML-KEM shared secrets
- derived session keys
- plaintext EHR payloads

Secrets must not appear in:

- JSONL
- CSV
- logs
- exception messages
- repr()
- plots

Use synthetic payloads and cryptographic operations only.

---

# 6. QKD Pool Model

Implement a deterministic synthetic QKD pool model.

The model must represent:

- pool capacity
- available key material
- generation/replenishment
- key consumption
- availability
- depletion
- outage

QKD generation rate and pool capacity are MODELED ASSUMPTIONS.

They are not claims about real-world QKD deployment.

Use configuration values rather than hard-coding values throughout the implementation.

The model must support the three pilot states:

- 100% availability
- 50% availability
- 0% availability

Availability must be controlled by the scenario configuration.

The QKD model must be deterministic for a fixed random seed.

---

# 7. QKD Availability Semantics

Define availability clearly.

100%:

QKD is available throughout the scenario.

50%:

QKD availability is constrained according to the scenario's deterministic
availability model.

0%:

No QKD material is available.

Do not interpret "50%" as a claim about physical QKD networks.

It is an experimental simulation condition.

---

# 8. ML-KEM Integration

Reuse the existing Task 5 ML-KEM implementation.

Use:

ML-KEM-768

Do not redesign the cryptographic implementation.

The experiment adapter must expose only what the simulator needs:

- key establishment
- shared-secret availability
- operation timing

Never store the actual shared secret in results.

---

# 9. ML-DSA Integration

Implement the authentication abstraction required by the baselines.

Use:

ML-DSA-65

The simulator needs to model the authentication operation consistently.

The authentication implementation must not become a separate research contribution.

Record:

- success/failure
- operation timing

Do not record:

- private signing keys
- signatures unless required for debugging
- secret material

---

# 10. Classical Baseline

Implement B1 using:

X25519
Ed25519
AES-256-GCM

B1 must use the same:

- workload
- network model
- transaction schedule
- metrics system

as B2–B5.

The purpose is baseline comparison, not a cryptographic benchmark.

---

# 11. PQC-only Baseline

Implement B2 using:

ML-KEM-768
ML-DSA-65
AES-256-GCM

B2 does not depend on QKD.

B2 must work identically at:

100%
50%
0%

QKD availability.

---

# 12. QKD-only Baseline

Implement B3 using:

QKD-derived key material
ML-DSA-65
AES-256-GCM

If QKD is unavailable:

B3 must explicitly report failure/blocking.

Do NOT silently replace QKD with ML-KEM.

The failure reason must be machine-readable.

---

# 13. Static Hybrid Baseline

Implement B4 using:

QKD
ML-KEM-768
ML-DSA-65
HKDF-SHA256
AES-256-GCM

Reuse the Task 6 hybrid combiner.

Do NOT create a second incompatible HKDF construction.

B4 requires both components.

If QKD is unavailable:

B4 must fail/block.

There is NO fallback.

---

# 14. Adaptive Baseline

Implement B5.

B5 is the primary proposed architecture.

At runtime:

if QKD is available:

    select HYBRID

else:

    select PQC_ONLY

B5 must expose its selected mode to the metrics layer.

Valid modes:

PQC_ONLY
HYBRID

Do not silently introduce additional modes.

The adaptive controller must make deterministic decisions based on scenario state.

---

# 15. Mode Synchronization

Create a mode synchronization abstraction.

The selected mode must be visible to:

- baseline execution
- metrics collector
- result writer

A mode change must never leave stale state from the previous mode.

The simulator must test transitions such as:

HYBRID → PQC_ONLY
PQC_ONLY → HYBRID

when the scenario permits them.

---

# 16. Synthetic EHR Workload

Create a synthetic EHR workload generator.

Never use real patient data.

Never generate realistic identifiable individuals.

The workload should represent EHR-inspired transaction behavior.

Transaction types:

- READ
- WRITE
- SHARE

Primary research emphasis:

SHARE

Criticality:

- ROUTINE
- EMERGENCY

Criticality is not a pilot axis.

---

# 17. Payload Classes

Support:

SMALL:
1–5 KB

MEDIUM:
20–80 KB

LARGE:
200 KB–1 MB

These are modeled assumptions.

Pilot uses:

MEDIUM only.

Payload generation must be deterministic for a fixed seed.

Use synthetic random bytes or equivalent non-sensitive data.

Never include generated plaintext payloads in result files.

---

# 18. Network Model

Implement a simplified 6G-edge abstraction.

Conceptual topology:

EHR client / IoMT
        |
6G access abstraction
        |
edge gateway
        |
hospital network
        |
EHR server

This is a simulation abstraction.

It is NOT a complete 6G protocol stack.

Model:

- network latency
- throughput
- packet loss
- network load
- edge processing delay

Pilot condition:

NOMINAL network load.

Do not claim these are real measured 6G values.

---

# 19. Transaction Execution

Every transaction must pass through the same high-level pipeline:

1. workload generation
2. baseline selection
3. key establishment
4. authentication
5. payload encryption
6. network transmission abstraction
7. result collection

The cryptographic difference between baselines must remain isolated from
the workload and network conditions.

---

# 20. Metrics

Collect at minimum:

- total latency
- key-establishment latency
- authentication latency
- encryption latency
- network latency
- success/failure
- failure reason
- selected mode
- payload size
- baseline
- QKD availability
- device count
- transaction type
- seed
- experiment ID

Do not record secrets.

---

# 21. Result Schema

Raw results:

JSON Lines.

Aggregated results:

CSV.

Each raw record should contain fields equivalent to:

experiment_id
baseline
seed
qkd_availability
device_count
payload_class
network_load
transaction_id
transaction_type
criticality
selected_mode
success
failure_reason
latency_ms
key_establishment_latency_ms
authentication_latency_ms
encryption_latency_ms
network_latency_ms
payload_bytes
qkd_pool_state

Never include:

private_key
shared_secret
qkd_key
session_key
plaintext

---

# 22. Reproducibility

Every experiment MUST require an explicit seed.

If the user attempts to run an experiment without a seed:

FAIL immediately.

Record:

- experiment ID
- seed
- configuration
- Git commit
- Python version
- dependency versions
- timestamp
- environment

Same:

configuration + seed

must produce equivalent deterministic simulation behavior.

---

# 23. Configuration

Do not hard-code experiment parameters.

Create:

experiments/configs/parameters.yaml

and appropriate pilot configuration files.

The pilot configuration must explicitly specify:

QKD availability:
100, 50, 0

device counts:
10, 1000

payload:
medium

network load:
nominal

baselines:
B1, B2, B3, B4, B5

repetitions:
5

The configuration must produce:

3 × 2 × 1 × 1 × 5 = 30 cells

with 5 repetitions per cell.

Do not add extra pilot axes.

---

# 24. Pilot Experiment

After implementation and unit/integration testing, execute the pilot.

Pilot:

3 QKD availability levels
×
2 device counts
×
1 payload
×
1 network load
×
5 baselines

= 30 configurations.

Use:

5 repetitions per configuration.

Total runs:

150 scenario repetitions.

Do NOT confuse:

30 configurations

with:

150 repeated executions.

---

# 25. Pilot Expansion Criteria

After the pilot, evaluate all six criteria.

### Criterion 1

All 30 configurations complete without unhandled errors.

### Criterion 2

Fairness audit passes.

### Criterion 3

B5 demonstrates switching between:

HYBRID
and
PQC_ONLY

at 50% QKD availability.

### Criterion 4

At 100% QKD availability:

B5 should behave comparably to B4.

At 0% QKD availability:

B5 should behave comparably to B2.

These are validation expectations, NOT guaranteed results.

### Criterion 5

Observed pilot variance is sufficiently controlled to distinguish the
planned experimental conditions.

### Criterion 6

Pilot runtime is feasible.

If any criterion fails:

STOP.

Do not expand the experiment.

Do not modify results to force criteria to pass.

Document the failure and recommended correction.

---

# 26. Statistical Processing

After raw pilot execution:

calculate:

- mean
- median
- standard deviation
- 95th percentile

For appropriate outcomes calculate:

95% bootstrap confidence intervals.

For pairwise non-parametric comparisons:

Mann-Whitney U

Apply appropriate multiple-comparison correction.

Use:

Bonferroni

or

Benjamini-Hochberg/FDR

depending on the comparison structure.

Do not automatically manufacture statistical significance.

If sample size or distribution makes a test inappropriate, document why.

---

# 27. Aggregation

Create:

experiments/src/metrics/aggregator.py

The aggregation layer must consume raw JSONL.

It must produce CSV.

Plots must consume the aggregated CSV rather than directly manipulating
raw experiment data.

This provides a reproducible:

raw → aggregate → plot

pipeline.

---

# 28. Plotting

Task 8 may generate pilot plots only after actual pilot execution.

Potential plots:

1. latency by baseline
2. latency by QKD availability
3. success rate by baseline
4. B5 selected mode by QKD availability
5. latency distribution
6. failure rate

Every plot must contain:

- clear axis labels
- units
- legend where required
- reproducible source data
- experiment configuration reference

Do not generate plots from fabricated data.

---

# 29. Fairness Audit

Implement a machine-checkable fairness audit.

Confirm that every baseline receives identical:

- workload
- transaction schedule
- device count
- payload
- network conditions
- seed policy
- measurement system

The only intended differences are cryptographic/key-management behavior
and resulting mode/failure behavior.

The audit must fail if configurations diverge unexpectedly.

---

# 30. Testing Requirements

Add unit tests for:

QKD pool
QKD availability
EHR generator
network model
baseline interface
B1
B2
B3
B4
B5
adaptive controller
mode synchronization
metrics
result schema
configuration loading
seed enforcement
fairness audit

Integration tests must verify:

B5 at 100% QKD → HYBRID

B5 at 0% QKD → PQC_ONLY

B3 at 0% QKD → FAILURE/BLOCKED

B4 at 0% QKD → FAILURE/BLOCKED

B2 at 0% QKD → SUCCESS

No secret material appears in serialized output.

---

# 31. Security and Research Integrity

This simulation does NOT prove cryptographic security.

Do not claim:

- formal QKD security
- formal ML-KEM security beyond its standardized primitive
- formal hybrid composability
- real-world QKD performance
- real-world EHR statistics
- real-world 6G performance

The simulator evaluates the defined engineering architecture under
controlled modeled conditions.

---

# 32. No Fabrication

Never create:

fake latency
fake throughput
fake success rates
fake p-values
fake confidence intervals
fake plots
fake benchmark tables

If a simulation fails, report the failure.

If a configuration cannot run, do not fabricate its output.

---

# 33. Documentation

Update:

docs/tasks/TASK_8.md

Document:

- implementation architecture
- baseline definitions
- workload model
- network model
- QKD model
- reproducibility
- metrics
- result schema
- pilot configuration
- pilot execution
- expansion decision

Only document actual results after the pilot has run.

Clearly separate:

DESIGN
IMPLEMENTATION
PILOT RESULTS
EXPANSION DECISION

---

# 34. Validation Before Pilot

Before running the pilot:

pytest

git diff --check

verify UTF-8

verify no mojibake

verify no secrets

verify no temporary files

verify seed enforcement

verify all five baselines

verify fairness audit

verify configuration count = 30

Do not run the pilot until these pass.

---

# 35. Git Discipline

Use a dedicated branch:

task-8/simulation-pilot

Do not modify main directly.

Before changes:

git status
git branch --show-current

After implementation:

git diff --check
pytest
git status

Do not create:

TASK-8.patch
diff.txt
temporary benchmark files

unless explicitly required for debugging; delete all temporary artifacts
before commit.

---

# 36. Completion Conditions

Task 8 is complete only when:

1. simulation framework exists;
2. all B1–B5 exist;
3. QKD pool exists;
4. adaptive controller exists;
5. workload generator exists;
6. network abstraction exists;
7. metrics pipeline exists;
8. reproducibility is enforced;
9. fairness audit passes;
10. all tests pass;
11. 30 pilot configurations execute;
12. five repetitions are executed per configuration;
13. raw JSONL results exist;
14. aggregated CSV results exist;
15. pilot plots are generated only from actual results;
16. six expansion criteria are evaluated;
17. expansion decision is documented.

If the pilot fails one or more expansion criteria, Task 8 should still
document the failure honestly and STOP before a full experiment.

---

# 37. Critical Stop Conditions

STOP immediately and report if:

- Task 6 must be redesigned;
- QKD key material cannot be accessed without changing Task 4 semantics;
- ML-KEM integration contradicts Task 5;
- B4 requires fallback behavior;
- B5 cannot reliably distinguish QKD availability;
- fairness cannot be guaranteed;
- deterministic execution cannot be achieved;
- secrets leak into results;
- the pilot produces unexplained inconsistent behavior;
- the 30-cell configuration cannot be executed reproducibly.

Do not silently work around these issues.

---

# 38. Final Report

At completion report:

- branch
- commit
- files created
- files modified
- test count
- test result
- configuration count
- repetitions
- total pilot executions
- runtime
- raw result location
- aggregated result location
- plot locations
- fairness audit result
- B5 switching validation
- B3/B4 failure validation
- B2 fallback-independent validation
- six expansion criteria
- expansion decision
- limitations
- unresolved research questions

The final report must clearly distinguish:

ACTUAL MEASUREMENTS

from

EXPECTED BEHAVIOR

from

MODELED ASSUMPTIONS.

Never present expected behavior as an observed result.