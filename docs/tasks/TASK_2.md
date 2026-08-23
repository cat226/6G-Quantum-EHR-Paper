# TASK 2 - Experimental Model and Interface Baseline

## 1. Objective

Define the formal software model and interfaces required for later
experiments on hybrid quantum-secure EHR sharing.

Task 2 establishes a technology-neutral experimental abstraction for:

- EHR transmission
- communicating entities
- security modes
- key-establishment state
- QKD availability
- PQC availability
- fallback behavior
- network conditions
- measurable performance metrics
- experiment configuration

Task 2 must NOT implement the actual QKD or PQC mechanisms.

The purpose is to ensure that subsequent implementations can be evaluated
using a common experimental interface.

---

## 2. Research Boundary

The repository is investigating a future 6G-oriented healthcare networking
context.

Task 2 must not assume that 6G is a finalized deployed standard.

The software model represents future network capabilities abstractly.

It must not claim that:

- a specific 6G architecture is standardized,
- a specific 6G security mechanism is mandatory,
- QKD is inherently superior to PQC,
- QKD + PQC integration is novel,
- a particular hybrid strategy is the optimal solution.

Those claims require later literature validation and experiments.

---

## 3. Experimental Entities

Define a minimal model for communicating entities.

The model should be capable of representing entities such as:

- EHR sender
- EHR receiver
- healthcare edge node
- medical/IoMT device
- key-management component

The model should remain generic.

Do not implement a complete hospital network.

The representation should allow later experiments to construct different
network topologies without modifying the underlying security interfaces.

---

## 4. EHR Transmission Model

Define a lightweight representation of an EHR transmission.

The model should capture only properties required for communication
experiments.

Potential fields include:

- transmission identifier
- payload size
- source
- destination
- timestamp or experiment sequence
- security mode

Do NOT include:

- real patient information
- real clinical records
- personally identifiable information
- medical diagnoses
- clinical decision logic

Payloads should be synthetic.

The model is intended to represent communication characteristics rather
than clinical content.

---

## 5. Security Mode Abstraction

Define a technology-neutral security-mode interface.

The interface must allow future implementations to represent at least:

1. PQC-only
2. QKD-only
3. Hybrid

The interface should expose the operations required by later experiments,
such as:

- key establishment
- availability/status
- estimated communication overhead
- security-mode identification

Do not implement the cryptographic algorithms in Task 2.

Do not hard-code claims about which mode is more secure.

---

## 6. QKD Availability Model

Define a representation of QKD key availability.

The model must be capable of representing at least:

- available
- unavailable
- insufficient key material
- degraded/limited availability

The exact QKD generation mechanism is outside Task 2.

QKD availability must be treated as an experimental input/state rather
than assumed to be continuously available.

This is important for future evaluation of fallback behavior.

Do not invent realistic QKD rates or availability percentages in Task 2.

---

## 7. PQC Availability Model

Define a corresponding abstract representation for PQC-based key
establishment.

The abstraction must allow future implementations to record:

- whether PQC key establishment succeeded
- establishment overhead
- latency
- failure state

Do not select a specific PQC algorithm in Task 2 unless it is required
solely for an interface identifier.

Algorithm selection belongs to a later implementation task and must be
supported by the research/literature methodology.

---

## 8. Hybrid Security Interface

The hybrid interface must NOT commit the research to one interpretation
of "hybrid."

It must allow future experimentation with multiple strategies, including:

### A. Simultaneous QKD + PQC

Both mechanisms participate in key establishment.

### B. PQC default + QKD additional layer

PQC provides the baseline while QKD provides an additional security
mechanism.

### C. QKD primary + PQC authentication/fallback

QKD is preferred when available while PQC provides authentication and/or
fallback functionality.

### D. Adaptive QKD/PQC switching

The system selects or switches security mechanisms according to network
conditions or QKD availability.

Task 2 only defines the interface necessary to represent these strategies.

It must not select one as the research conclusion.

---

## 9. Network Condition Model

Define a generic network-condition representation for future simulation.

Potential variables include:

- propagation/communication latency
- bandwidth
- packet loss
- congestion/load
- edge processing delay
- QKD availability
- key-material availability

Do not assign empirical values to these variables.

Use configurable values or neutral placeholders.

Empirical parameter selection belongs to later experimental methodology
and literature validation.

---

## 10. Metrics Interface

Define the metrics that later experiments must be able to collect.

At minimum support conceptual measurement of:

### Security-related

- security mode
- key-establishment success/failure
- QKD availability
- fallback events

### Performance-related

- key-establishment latency
- EHR transmission latency
- communication overhead
- processing overhead where measurable

### Scalability-related

- number of concurrent entities/sessions
- number of EHR transmissions
- network load
- key-material demand

The implementation should provide data structures/interfaces for recording
metrics.

Task 2 must not produce research results.

---

## 11. Experiment Configuration

Extend the existing configuration architecture sufficiently to describe
future experiments.

Configuration should support categories such as:

```yaml
experiment:
  seed:
  mode:
  number_of_sessions:

network:
  latency:
  bandwidth:
  packet_loss:

qkd:
  availability:
  key_material:

ehr:
  payload_size: