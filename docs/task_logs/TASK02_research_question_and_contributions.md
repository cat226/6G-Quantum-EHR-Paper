# TASK 2 — Research Question and Contributions

**Project:** 6G-Enabled Hybrid Quantum-Secure Architecture for Electronic
Health Record Sharing
**Authors:** Ramana Sree K V, Verona Ann Mariya
**Status:** Draft for approval — precedes literature validation (Task 3)
**Depends on:** Task 1 (Project Audit) — approved

**Epistemic status of this document:** Everything below is a candidate
research direction, not a validated one. No literature search has been
performed. Every novelty label, every claim about what "existing
approaches" look like, and every assumption is explicitly flagged as
provisional and subject to revision or rejection once Task 3 (Literature
Database) and Task 4/5 (State of the Art / Research Gap) produce
evidence.

---

## 1. Problem Statement

Electronic Health Records (EHRs) carry information whose confidentiality
must typically be protected for years to decades after creation, driven
by patient lifespans and jurisdiction-specific retention requirements.
This long confidentiality lifetime is significant in the context of the
"harvest-now, decrypt-later" threat model: data encrypted today with
classical public-key cryptography (RSA/ECC-based key exchange and
signatures) could be recorded by an adversary now and decrypted once a
cryptographically relevant quantum computer becomes available, even if
that capability does not yet exist. This is a distinct concern from
generic "quantum threats to healthcare" — it specifically implicates
any EHR exchange mechanism that relies on classical asymmetric
cryptography for key establishment or authentication, regardless of
when the underlying quantum capability actually materializes.

Two broad classes of quantum-resistant key-establishment mechanism
exist today: Quantum Key Distribution (QKD), which offers
information-theoretic key-exchange security guarantees but requires
specialized hardware, has practical transmission-distance limits, and
is fundamentally point-to-point rather than naturally suited to
many-to-many topologies; and Post-Quantum Cryptography (PQC), which is
deployable on ordinary computing/network infrastructure (NIST finalized
ML-KEM, ML-DSA, and SLH-DSA as standards in 2024) but relies on
computational hardness assumptions rather than information-theoretic
guarantees, and introduces larger key/ciphertext/signature sizes than
classical algorithms. Healthcare data exchange increasingly involves
heterogeneous, latency-sensitive, resource-constrained environments —
medical IoT devices, edge computing nodes, and (prospectively) networks
built on 6G, whose standards are not yet finalized (the ITU-R's IMT-2030
framework recommendation, approved in 2023, defines a usage-scenario
vision, while 3GPP standardization and commercial deployment are
anticipated toward the end of this decade — not present-day realities).
This paper therefore treats "6G-enabled" as a forward-looking network
context characterized by anticipated properties (e.g., very low latency,
high device density, native support for distributed/edge intelligence)
that will be explicitly modeled as assumptions, not as a claim about an
existing, standardized, deployable network.

The problem this project investigates is whether and how QKD and PQC
mechanisms can be combined into a key-establishment approach for EHR
sharing across such an edge-assisted, 6G-anticipated healthcare network
topology, in a way that (a) provides quantum-resistant confidentiality
guarantees that neither mechanism achieves alone under realistic
deployment constraints, (b) remains operable across heterogeneous nodes
that may not all have QKD hardware, and (c) does so within latency and
overhead bounds compatible with time-sensitive clinical workflows. This
document does not assert that this problem is unaddressed in the
existing literature — that determination is deferred to Tasks 3–5.

---

## 2. Main Research Question

> **For EHR exchange across an edge-assisted, 6G-anticipated healthcare
> network, how does a hybrid QKD-PQC key-establishment approach compare
> to PQC-only, QKD-only, and classical baselines in terms of (a) key
> establishment latency, (b) end-to-end EHR transmission latency and
> communication overhead, and (c) continuity of secure operation
> (successful fallback rate) when QKD channel availability is degraded
> or interrupted — and under what conditions, if any, does the hybrid
> approach provide a measurable advantage over the non-hybrid
> baselines?**

This question is deliberately comparative and conditional rather than
presupposing an answer. It is investigable through simulation (network
topology + key-establishment logic + measured cryptographic operation
timings), does not require physical QKD hardware, and yields concrete,
measurable outputs (latency figures, overhead figures, a fallback
success-rate metric) rather than a qualitative judgment.

---

## 3. Research Objectives

1. **O1 — Specify the architecture and protocol.** Produce a complete
   technical specification (including pseudocode) of a hybrid QKD-PQC
   key-establishment and EHR-encryption protocol for the target
   topology, explicitly defining key generation, mutual authentication,
   key derivation, and fallback behavior when QKD is unavailable.
   *Measurable via:* completeness against a defined interface/behavior
   checklist (produced in Task 6/8); reviewable independent of any
   simulation results.

2. **O2 — Build a reproducible simulation environment.** Implement a
   simulation covering network topology, key-establishment logic, and
   EHR-sized payload encryption, capable of running the hybrid design
   and at least two baselines (classical; PQC-only; QKD-only if
   technically tractable) under controlled, repeatable configurations.
   *Measurable via:* identical configs reproducing results within
   defined stochastic bounds; code and configs version-controlled in
   `experiments/` and `simulation/`.

3. **O3 — Quantify latency and communication overhead.** Measure key
   establishment latency and end-to-end EHR transmission
   latency/overhead for the hybrid design versus baselines, across a
   defined set of network conditions (e.g., node count, QKD link
   availability, EHR payload size).
   *Measurable via:* numeric results tables/plots generated directly
   from simulation runs in `experiments/results/`, never asserted
   without an underlying run.

4. **O4 — Quantify resilience under QKD disruption.** Measure the
   success rate and latency impact of PQC fallback when the QKD channel
   is deliberately disrupted in simulation, compared against a
   QKD-only baseline under identical disruption conditions.
   *Measurable via:* a defined fallback-success-rate metric across a
   matrix of disruption scenarios (e.g., intermittent vs. sustained
   outage).

5. **O5 — Produce an evidence-based, non-overclaiming threat model.**
   Define which threats the hybrid design mitigates, which it does not,
   and which require complementary (non-cryptographic) controls,
   explicitly avoiding the claim that QKD alone secures the system.
   *Measurable via:* a completed threat-model table (attacker
   capability → target → attack surface → consequence → mitigation)
   with no unsupported entries.

These five objectives are intentionally scoped to be achievable via
simulation and measurement rather than requiring physical hardware,
consistent with the feasibility constraints discussed in Section 7.

---

## 4. Candidate Contributions

For each candidate contribution: what exactly would be contributed,
what evidence would be needed to support it, its type, and its
**provisional** novelty label. No contribution is labeled **A
(potentially novel)** in this document, because that determination
requires literature evidence not yet gathered. Labels below reflect the
most defensible provisional assessment and are explicitly subject to
revision after Task 3/4/5.

### C1 — A hybrid QKD-PQC key-management architecture specified for EHR sharing over an edge-assisted, 6G-anticipated topology
- **What exactly:** A concrete architecture (components, interfaces,
  trust boundaries, control/data plane separation) applying a hybrid
  QKD-PQC key-establishment approach specifically to EHR exchange
  across medical IoT/edge/6G-anticipated infrastructure, including
  explicit fallback behavior.
- **Evidence needed:** Task 3/4 must establish whether a
  near-identical architecture (hybrid QKD-PQC, applied specifically to
  healthcare/EHR, with an explicit edge/6G framing) already exists. If
  so, this contribution narrows to an adaptation/refinement rather than
  a new architecture.
- **Type:** Architectural.
- **Provisional label:** **B — likely an integration contribution.**
  Combining QKD and PQC for key establishment is a documented general
  idea outside healthcare (e.g., hybrid key-exchange work in networking
  and telecom contexts); applying it to the EHR/edge/6G-healthcare
  combination specifically may be new as an *integration*, not
  necessarily as a *technique*.

### C2 — A quantitative comparison using EHR-representative workloads
- **What exactly:** Simulation-based latency/overhead comparison of
  hybrid vs. PQC-only vs. QKD-only vs. classical approaches, using
  payload sizes and latency budgets representative of actual clinical
  data exchange (e.g., FHIR-bundle-scale messages) rather than generic
  network-benchmark traffic.
- **Evidence needed:** Sourced data (not invented) on typical EHR
  message/FHIR bundle sizes and clinically relevant latency
  requirements; confirmation of whether a comparable EHR-representative
  benchmark of hybrid quantum-safe key exchange already exists.
- **Type:** Experimental / methodological.
- **Provisional label:** **B/C — mixed.** The benchmarking methodology
  itself (multi-baseline latency/overhead comparison) is standard
  practice (C); applying it with EHR-shaped workload assumptions in
  this specific combined context is, at best, a modest integration
  contribution (B), contingent on Task 3 finding no existing equivalent.

### C3 — Measured resilience/fallback behavior under simulated QKD disruption
- **What exactly:** Not merely proposing "PQC as fallback when QKD is
  unavailable" as a concept, but implementing and quantitatively
  measuring fallback behavior (success rate, latency impact, any
  transition-period exposure) under simulated QKD channel disruption in
  a healthcare-network context.
- **Evidence needed:** Task 3 must determine whether adaptive/fallback
  QKD-PQC switching (Option D in Section 5) has already been proposed
  and evaluated in any domain; if so, in what domain and with what
  results, which determines whether this becomes an application-context
  contribution rather than a mechanism contribution.
- **Type:** Experimental / analytical.
- **Provisional label:** **B — likely an integration/evaluation
  contribution**, not a new switching mechanism.

### C4 — A threat model specific to the hybrid design in this context
- **What exactly:** An explicit threat model distinguishing which
  threats are mitigated by QKD, by PQC, by neither, and which require
  complementary controls (device/endpoint security, access control),
  tailored to the edge/6G-anticipated/EHR context.
- **Evidence needed:** Verification (not assumption) of commonly cited
  QKD caveats — e.g., that QKD's security guarantee depends on the
  classical channel used to authenticate it, which must itself be
  authenticated by some other mechanism — before this is used as a
  design justification; and a check for existing threat models covering
  hybrid quantum-safe or healthcare-IoT systems.
- **Type:** Analytical.
- **Provisional label:** **C/B — mixed.** Threat modeling for hybrid
  quantum-safe systems is a standard analytical technique (C); tailoring
  it precisely to this combination of context factors may be a minor
  integration contribution (B) if the literature has not already done
  so.

### C5 — A reproducible reference simulation implementation
- **What exactly:** Open, version-controlled simulation code and
  configuration usable as a baseline testbed for further
  healthcare-quantum-security research, covering the architecture in
  C1 and the measurements in C2–C4.
- **Evidence needed:** Not a novelty claim — but Task 3/4 should check
  whether comparable open testbeds already exist, so the write-up does
  not imply originality that has not been verified.
- **Type:** Experimental (research artifact).
- **Provisional label:** **C — standard/known technique** (building a
  reproducible testbed is standard research infrastructure; its value
  here is reproducibility, not originality).

**Summary:** No contribution is currently claimed as fundamentally
novel. The most defensible framing, pending Task 3–5 evidence, is that
this project's value lies in a specific, evidence-grounded **integration
and quantitative evaluation** of already-known building blocks (QKD,
PQC, edge computing, EHR exchange) in a combination and context that may
not yet have been jointly and empirically evaluated — a claim that
itself still requires literature verification before it can be stated
in the manuscript.

---

## 5. The Current Ambiguity Around "Hybrid"

Four candidate technical meanings of "hybrid QKD-PQC" are analyzed
below. None is selected as final in this document.

### A. QKD and PQC used simultaneously for every key establishment
- **Technical meaning:** Both mechanisms run for every session; the
  final symmetric key is derived by combining a QKD-derived key and a
  PQC-KEM-derived key through a key-derivation function (analogous to
  hybrid classical/PQC key-exchange combiners explored in TLS 1.3
  drafts, generalized to include a QKD input).
- **Advantages:** Strongest defense-in-depth — compromise of either
  mechanism alone does not break the session key (assuming a secure
  combiner); provides both information-theoretic and computational
  security properties simultaneously.
- **Disadvantages:** Requires a QKD link to be available for *every*
  key establishment, which is unrealistic for most edge/IoT nodes;
  highest protocol complexity and latency (bounded by the slower of the
  two mechanisms, typically QKD); assumes universal QKD reach that
  contradicts QKD's known distance/hardware constraints.
- **Implementation complexity:** High.
- **Relevance to EHR sharing:** Plausible only for a small number of
  fixed, high-value backbone links (e.g., hospital-to-hospital core
  network); poor fit for the medical-IoT/edge portion of the topology.
- **What would need to be measured:** Key-establishment latency and
  overhead under an always-available-QKD assumption; security margin
  and correctness of the key combiner.

### B. PQC as default, QKD as an additional security layer where available
- **Technical meaning:** Primary session keys and authentication are
  established via PQC (KEM + signatures). Where a QKD channel exists
  (e.g., select backbone links only), QKD-derived material is used to
  periodically re-key or add entropy, but the system is fully
  functional using PQC alone everywhere.
- **Advantages:** Naturally accommodates partial/heterogeneous QKD
  deployment, which matches QKD's real-world reach; lower baseline
  latency/overhead since QKD use is opportunistic; graceful degradation
  is inherent rather than a special-cased fallback.
- **Disadvantages:** The security benefit attributable to QKD only
  applies to the subset of links where it is deployed — most of an
  edge/IoT path may never benefit from it; requires precise definition
  of which segments are QKD-eligible.
- **Implementation complexity:** Medium (PQC-only baseline is
  straightforward using existing libraries; QKD augmentation can be
  added incrementally and in isolation).
- **Relevance to EHR sharing:** Good fit given QKD's known range/
  hardware constraints; plausibly the most deployable option for a
  mixed hospital-backbone + medical-IoT-edge topology.
- **What would need to be measured:** Incremental security/latency
  benefit attributable to QKD-augmented links versus PQC-only links;
  the fraction of a realistic end-to-end path that is actually
  QKD-eligible.

### C. QKD as primary key source with PQC for authentication/fallback
- **Technical meaning:** Mirrors standard QKD deployment practice, in
  which QKD protocols (e.g., BB84) require an authenticated classical
  channel — traditionally provided by pre-shared keys or classical
  PKI. Here, PQC signatures would authenticate that classical channel
  (replacing a quantum-vulnerable classical-PKI step), and PQC key
  establishment is used as the complete fallback mechanism for any
  session where the QKD link is unavailable, degraded, or exhausted.
- **Advantages:** Uses QKD where it is deployed for its strongest use
  case (link-level key material); explicitly closes a commonly cited
  QKD deployment gap (its security is bounded by the strength of the
  classical channel authenticating it) — though this claim about QKD
  itself must be verified against the literature in Task 3, not assumed
  here; produces a direct, well-defined "fallback event" that maps
  cleanly onto Objective O4 (resilience measurement).
- **Disadvantages:** On QKD-ineligible links (likely the majority of
  the topology), the system is functionally identical to PQC-only,
  which narrows where "hybrid" behavior is actually observable;
  requires explicit disruption-detection and fallback-triggering logic,
  adding protocol-state complexity.
- **Implementation complexity:** Medium-high (requires modeling QKD
  channel availability/failure explicitly, plus a defined state machine
  for fallback and key-source labeling).
- **Relevance to EHR sharing:** Strong alignment with the research
  question as currently formulated, since it directly produces the
  resilience/fallback metric in O4 and cleanly connects to the
  harvest-now-decrypt-later and QKD-deployment-limitation framing in
  the problem statement.
- **What would need to be measured:** Fallback-trigger latency;
  security continuity across the QKD→PQC transition (whether any key
  material is exposed mid-transition); frequency/duration of fallback
  events under simulated disruption profiles.

### D. Adaptive switching between QKD and PQC based on network conditions
- **Technical meaning:** A policy/control-plane component dynamically
  selects QKD, PQC, or both per session or per link based on real-time
  inputs — link quality, latency budget, data criticality, or QKD
  key-pool availability.
- **Advantages:** Most flexible; can, in principle, optimize the
  security/latency/availability trade-off at runtime; generalizes
  Options A–C as special-case policies.
- **Disadvantages:** By far the most complex option to design,
  implement, and evaluate; introduces new attack surface (the
  policy/controller logic itself, e.g., forced-downgrade attacks that
  trick the system into a weaker mode); requires a non-trivial,
  evidence-backed policy model to avoid being ad hoc; likely exceeds
  the feasible scope of a 2–3 month, two-person project (see Section
  7).
- **Implementation complexity:** Highest of the four options.
- **Relevance to EHR sharing:** Attractive in principle (e.g.,
  life-critical alerts vs. routine record synchronization could
  justify different policies) but probably better suited to future work
  than the core contribution of this project.
- **What would need to be measured:** Policy decision correctness and
  latency; resistance to forced-downgrade attacks; end-to-end metrics
  across a combinatorially larger scenario matrix than Options A–C.

**No option is selected here.** Section 9 provides a provisional,
feasibility-driven (not literature-driven) working default to guide
Task 3 search terms only.

---

## 6. Scope — What This Paper Will NOT Attempt to Solve

- Physical implementation or deployment of QKD hardware (simulation/
  modeling only; no access to real QKD hardware is assumed).
- Complete 6G standardization, or any claim about a finalized,
  deployed 6G network (6G characteristics used in this project are
  explicitly modeled assumptions, sourced from anticipated-standards
  literature where possible, not deployment facts).
- Comprehensive security of every component of a hospital's IT
  environment (e.g., EHR database-at-rest security, physical security,
  staff training, non-cryptographic operational security are out of
  scope except where they appear as boundary conditions in the threat
  model).
- Clinical decision-making, diagnostic accuracy, or any patient-level
  medical outcome.
- Production-grade deployment, certification, or formal regulatory
  compliance auditing (e.g., HIPAA/GDPR compliance certification),
  though relevant regulatory context may be cited to justify retention/
  latency assumptions.
- Design of novel cryptographic primitives — only existing standardized
  or candidate PQC algorithms (e.g., ML-KEM/ML-DSA) and modeled,
  literature-grounded QKD protocols (e.g., BB84) will be used.
- Formal, reduction-based cryptographic security proofs — the security
  analysis will be a structured, informal threat-model analysis (per
  Objective O5), not a formal proof.
- Real quantum-hardware experiments — all quantum aspects are
  simulated/modeled (e.g., via Qiskit at the protocol/logical level),
  not run on physical quantum devices.
- An exhaustive enumeration of every conceivable attack — the threat
  model will cover a defined, explicit, justified list of threats
  (Task 7), not claim completeness.
- Multi-hospital, multi-vendor, real-world interoperability testing.

---

## 7. Feasibility Assessment (2–3 Months, Two Researchers)

**Overall assessment:** A simulation-based study of a hybrid QKD-PQC
key-establishment approach (most plausibly Option B or C from Section
5), incorporating real measured PQC benchmark timings, literature-
grounded modeled QKD parameters, a defined threat model, and a focused
comparison against 2–3 baselines, appears **feasible** within 2–3
months for two researchers — **provided** scope is held tightly to
Section 6 and Option D (Section 5) is deferred to future work. This
assessment may need revision after Task 3 if, for example, no usable
QKD parameter data exists in the open literature, or an existing
testbed makes the experimental contribution redundant.

### What can realistically be simulated
- Network topology and latency modeling (e.g., via SimPy or a
  lightweight custom discrete-event simulator).
- PQC computational overhead — **can be genuinely measured**, not just
  modeled, using a real PQC library (e.g., liboqs bindings) to time
  key generation, encapsulation/decapsulation, and signing/verification
  on available hardware.
- QKD protocol behavior at the logical/protocol level (e.g., BB84
  sifting simulation via Qiskit or a custom simulator), producing a
  modeled key-generation rate.
- EHR-shaped payload encryption/decryption overhead, using real
  encryption libraries on synthetic/representative payloads.
- Fallback/switching logic, as software logic within the simulation.

### What requires real hardware (and is therefore excluded)
- Actual QKD hardware links (single-photon sources/detectors,
  dedicated fiber) — not available to a student project.
- A real 6G radio access network — does not yet exist; cannot be
  tested, only modeled.
- Real medical IoT devices in a clinical setting — out of scope;
  representative/synthetic workload models will be used instead.

### What can be modeled (with cited, not invented, parameters)
- 6G link characteristics (latency/throughput ranges), modeled from
  published anticipated-6G parameter ranges (to be sourced in Task 3)
  and clearly labeled as forward-looking assumptions.
- QKD physical-layer behavior (key-generation rate vs. distance,
  channel loss), modeled from published QKD experimental/theoretical
  parameter ranges (Task 3), not invented.
- Network scale (tens to low hundreds of nodes, representing a regional
  rather than national healthcare network), chosen for simulation
  tractability and justified as such, not presented as a
  general-scale claim.

### What should be excluded given the timeline
- Option D (adaptive multi-factor switching) — deferred to future work.
- Formal/mathematical security proofs — an informal, structured threat-
  model analysis will be used instead.
- A large-scale, multi-variable statistical design-of-experiments sweep
  — evaluation will use a focused, justified set of scenarios (Task 9),
  not exhaustive coverage.
- Any real clinical/patient data — synthetic, representative EHR-shaped
  payloads only (e.g., based on public FHIR examples), avoiding any
  human-subjects or data-governance overhead.

---

## 8. Literature Dependencies for Task 3

For every major claim or contribution above, the following evidence
must be found (or its absence explicitly noted) before it can be
accepted:

**For the problem statement:**
- Evidence for EHR/healthcare data's long confidentiality-retention
  requirements (regulatory/domain sources).
- Evidence for the current quantum-threat/PQC-standardization status
  (NIST ML-KEM/ML-DSA/SLH-DSA) to ground "quantum threat" claims in
  fact.
- Evidence for 6G's actual standardization status (ITU-R IMT-2030,
  3GPP timeline) to correctly frame 6G as anticipated, not deployed.
- Evidence on medical IoT/edge computing constraints relevant to
  healthcare (compute/power/latency).

**For research-gap validity (feeds Task 4/5):**
- Evidence of existing QKD-for-healthcare architectures (or their
  absence).
- Evidence of existing PQC-for-healthcare/EHR architectures and their
  stated limitations (or absence).
- Evidence of existing hybrid QKD-PQC proposals, in any domain, and
  specifically in healthcare (or absence) — critical for the C1–C4
  novelty labels above.
- Evidence of existing 6G-healthcare-security proposals and their
  security assumptions (or absence).
- Evidence of existing EHR-specific security architectures (access
  control, blockchain-EHR, cloud/edge EHR security) and whether any
  already address quantum threats.
- Evidence of edge-assisted quantum-safe security proposals in any
  domain.

**Per candidate contribution (Section 4):**
- C1: whether a near-identical hybrid QKD-PQC EHR/edge/6G architecture
  already exists.
- C2: sourced EHR/FHIR message-size and clinical-latency-requirement
  data; whether an EHR-representative comparison of this kind already
  exists.
- C3: whether adaptive/fallback QKD-PQC switching has already been
  proposed/evaluated, in what domain, and with what results.
- C4: verification of the QKD classical-channel-authentication caveat
  as an actual documented limitation (not an assumption); existing
  threat models for hybrid quantum-safe or healthcare-IoT systems.
- C5: whether a comparable open-source QKD-PQC-healthcare simulation
  testbed already exists.

**For the "hybrid" definition (Section 5):**
- How established literature (e.g., IETF hybrid key-exchange drafts,
  telecom/networking hybrid QKD-PQC proposals) defines "hybrid," so
  this project's terminology aligns with or explicitly diverges from
  existing usage rather than inventing inconsistent terms.
- Reported data on QKD range/hardware/deployment constraints, to
  confirm (not assume) the practicality concerns raised against Option
  A.

**For feasibility assumptions (Section 7):**
- Published QKD key-generation-rate-vs-distance parameter ranges.
- Published/anticipated 6G latency and throughput target ranges
  (ITU-R/3GPP sources).
- Published PQC algorithm performance benchmarks, to contextualize
  (not replace) this project's own measured PQC timings.

---

## 9. Final Recommendation

- **Recommended research question:** As stated in Section 2.

- **Recommended objectives:** O1–O5 as stated in Section 3.

- **Recommended contribution set:** C1–C5 as stated in Section 4, all
  currently labeled B or C (no A), explicitly provisional pending Task
  3–5 evidence. The most defensible current framing is an
  **evidence-grounded integration and quantitative evaluation**
  contribution, not a fundamentally new technique — this framing itself
  still requires literature verification before being stated in the
  manuscript.

- **Recommended definition of "hybrid," IF justified:** **Not yet
  literature-justified — no option in Section 5 is selected.** As a
  *feasibility-driven, provisional working default* to guide Task 3
  search terms only (not a final architectural decision), **Option C
  (QKD as primary key source with PQC for authentication/fallback)**
  is the best current fit: it aligns most directly with the research
  question's resilience axis (O4), produces a cleanly measurable
  fallback event, and has a bounded implementation complexity
  consistent with the feasibility assessment in Section 7. This must be
  revisited once Task 3 evidence is available — in particular, evidence
  about QKD's classical-channel-authentication dependency and about
  what "hybrid" means in existing literature could shift this toward
  Option B, or reveal that Option C already exists in near-identical
  form elsewhere.

- **What must be verified in Task 3 (highest priority items):**
  1. Whether hybrid QKD-PQC healthcare/EHR architectures already exist
     in a form close to what is proposed here — this single finding
     most affects whether the project proceeds as currently scoped or
     needs reframing (e.g., toward "first quantitative resilience
     evaluation of X in a healthcare/edge context" rather than "a
     hybrid architecture").
  2. Whether the QKD classical-channel-authentication caveat used to
     motivate Option C is an established, citable limitation.
  3. Sourced parameter ranges for QKD key-generation rate vs. distance
     and for anticipated 6G latency/throughput, without which the
     simulation's modeled inputs cannot be responsibly justified.
  4. Sourced EHR/FHIR workload-size and clinical-latency-requirement
     data, without which Contribution C2 cannot be claimed as
     "EHR-representative."
  5. Existing terminology/precedent for "hybrid" QKD-PQC key exchange
     in networking/telecom literature, to align this project's
     definitions with established usage.

- **Recommendation on the title:** **Retain the current title as a
  working title for now; do not finalize it.** Two caveats to carry
  forward: (a) "6G-Enabled" must be explicitly scoped in the
  Introduction as targeting anticipated 6G characteristics via
  simulation, not real 6G deployment — this does not require a title
  change but does require clear framing language; (b) the title's
  implicit claim of a novel "hybrid architecture" is not yet supported
  and must be checked against Task 3–5 findings. If Task 3 finds
  near-identical existing hybrid QKD-PQC EHR architectures, the framing
  (and possibly the title) should shift toward emphasizing this
  project's specific, verifiable contribution (e.g., a simulation-based
  resilience/latency evaluation in an edge-assisted context) rather
  than implying the architecture itself is new. Final title wording
  should be revisited after Task 5, once the research gap is verified
  rather than assumed.

---

**TASK 2 COMPLETE — AWAITING APPROVAL.**
