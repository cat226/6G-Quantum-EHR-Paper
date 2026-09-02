# TASK 5 — RESEARCH GAP, FINAL RESEARCH QUESTION, AND CONTRIBUTION

**Basis:** the collision table and A–G labels from `TASK05_novelty_collision_analysis.md`
(papers P1–P11, this session's live search). Nothing below assumes 6G+QKD+PQC+EHR
is novel as a combination — that claim was rejected in the prior pass.
**Standing caveat, carried forward:** this rests on ~15 targeted searches this
session, not the full 30–50 paper systematic pass. Treat "not found" as "not
found by this pass," and re-run the Task 3 per-paper verification checklist
on P1, P2, P5, P6, P8 before anything here is cited in the actual paper.

---

## 1. Literature-based gap analysis

**Gap 1 — Adaptive/failure-aware QKD-PQC switching is proven for critical
infrastructure, never evaluated for healthcare/EHR.**
- Existing: P5 (Spooren et al. 2026, IEEE QCNC — layered fail-safe QKD+PQC,
  uninterrupted multi-hop operation), P8 (Zhu 2025 — stochastic SLA/
  availability modeling comparing Hybrid vs. QKD-only vs. PQC-only for
  power-grid GOOSE/PMU traffic, with explicit fallback-fraction analysis).
- What they accomplish: prove the fallback mechanism works, is
  measurable, and improves availability over single-mode approaches — for
  power-grid and generic multi-hop traffic.
- What they do NOT evaluate: healthcare/EHR traffic patterns, EHR-specific
  latency criticality (routine vs. emergency access), IoMT/6G-edge
  topology, healthcare-relevant availability thresholds.
- Evidence strength: strong for the general mechanism (two independent,
  methodologically rigorous 2025–2026 papers); zero direct healthcare
  evidence.
- Why it matters: power-grid traffic (GOOSE/PMU) and EHR traffic have
  different latency/criticality profiles — P8's thresholds and parameter
  regimes are not guaranteed to transfer without new evaluation.
- Research-worthy: yes, if the EHR workload model is real (not just
  power-grid data relabeled).
- Feasible for two students, 2–3 months: yes — simulation-based, no new
  hardware.

**Gap 2 — Field-validated QKD+PQC-for-healthcare architectures exist, but
all are static; none evaluate behavior under QKD unavailability.**
- Existing: P1 (Roosan et al. 2025 — DAG-ledger + QKD + PQC for
  telehealth), P2 (Papadopoulos et al. 2026, IEEE Access — real hybrid
  QKD-PQC pilot for off-site hospital data), P3 (arXiv 2608.18869 — 140 km
  field-deployed QKD+PQC link, rural health kiosk to university hospital).
- What they accomplish: demonstrate hybrid QKD+PQC for healthcare data is
  deployable and functional, from simulation (P1) to real field pilot
  (P2, P3).
- What they do NOT evaluate: behavior when the QKD channel degrades or
  drops (P2's fallback behavior is unverified — full text unread; P3 is a
  single fiber link, not tested under induced outage).
- Evidence strength: strong that "QKD+PQC-for-healthcare works under
  nominal conditions"; no evidence on degraded-mode behavior in this
  domain.
- Why it matters: healthcare access can't simply block when a QKD link
  drops — if fallback is required, it should be designed against EHR
  criticality, not assumed safe by analogy to other domains.
- Research-worthy: yes — this is the direct justification for the
  selected direction below.
- Feasible: yes.

**Gap 3 — 6G+QKD+PQC already exists at the network-authentication layer;
claiming the triple combination itself as the contribution is the
weakest possible framing.**
- Existing: P6 (Atutxa, Sanz et al. 2025 — PQC-authenticated QKD classical
  channel in a multi-site 5G/6G network).
- What it accomplishes: proves 6G+QKD+PQC is not conceptually novel at
  the network layer.
- What it does not evaluate: any application-layer healthcare workload,
  EHR data, IoMT endpoints, or adaptive fallback.
- Evidence strength: strong on the network-layer combination; none on
  application.
- Why it matters: this is direct evidence against Direction A below —
  not a gap to pursue, but a reason to rule one out.
- Research-worthy as a standalone claim: no.
- Feasible: N/A — folds into Gaps 1–2.

**Gap 4 — EHR-specific hybrid key management exists for PQC-only, never
extended with QKD or adaptive behavior.**
- Existing: P10 (Mahesh & Mishra 2025, *PCBQC* — patient-centric EHR,
  blockchain-anchored, combining multiple lattice-PQC algorithms).
- What it accomplishes: patient-centric EHR key/access management with
  PQC.
- What it does not evaluate: any QKD component, any 6G/edge topology, any
  latency-under-load or availability analysis.
- Evidence strength: moderate — single paper, non-IEEE venue (*Int J
  Performability Eng*), not independently corroborated; still owes
  full-text verification.
- Why it matters: confirms EHR-specific PQC key management is an active,
  legitimate research pattern — extending it with QKD and adaptivity is a
  recognizable next step, not an invented sub-field.
- Research-worthy: moderate — useful as a design reference/baseline, not
  a standalone gap.
- Feasible: yes, as reference only.

**Gap 5 (weaker, flagged) — No paper found does a systematic multi-
objective (security/latency/overhead) trade-off characterization for
hybrid QKD-PQC, in any domain.**
- Existing: P8 and a TLS-benchmarking literature review report point
  comparisons at fixed configurations (e.g., one review cites a hybrid
  PQC-QKD TLS handshake latency increase around 117% at one operating
  point) rather than a systematic sweep.
- What they accomplish: quantify tradeoffs at specific operating points.
- What they do not evaluate: the full trade-off surface across
  simultaneously varying QKD availability, payload size, and device
  count.
- Evidence strength: weak positive (absence-based, single supplementary
  search) — genuinely not found, but not deeply searched for either.
- Why it matters: if true, systematic multi-dimensional characterization
  is itself an under-done *evaluation methodology*, independent of
  domain.
- Research-worthy: yes, but as an evaluation lens layered onto Gaps 1–2,
  not as a standalone architectural claim.
- Feasible: yes — this is an experiment-design choice, not new
  infrastructure.

---

## 2. Candidate direction evaluation

**A. Generic 6G+QKD+PQC+EHR architecture**
- Existing overlap: High (P1/P2/P3 + P6 together span this combination).
- Novelty potential: **LOW**
- Technical feasibility: High
- Required experiment: N/A as a bare architecture claim
- Measurable metrics: N/A as stated
- Main risk: reads as recombination of existing pieces
- Recommendation: do not pursue as the core framing

**B. Static hybrid QKD-PQC EHR security**
- Existing overlap: High, direct — P1 and P2 already do close to this
- Novelty potential: **LOW**
- Technical feasibility: High
- Required experiment: implement classical/PQC/QKD/static-hybrid
  baselines, single-point latency/overhead measurement
- Measurable metrics: key establishment latency, throughput, overhead
- Main risk: duplicates P1/P2's contribution shape
- Recommendation: usable only as a **baseline** inside a larger study,
  not as the paper's core claim

**C. Adaptive QKD-PQC key management (no healthcare scoping)**
- Existing overlap: Medium–High (P5, P8 already do this generically)
- Novelty potential: **LOW**
- Technical feasibility: High
- Required experiment: simulate mode-switching under varying QKD
  availability
- Measurable metrics: fallback rate, transition latency, key
  availability
- Main risk: without a new domain/constraint, duplicates P5/P8
- Recommendation: fold into E; not viable standalone

**D. QKD-availability-aware PQC fallback (no healthcare scoping)**
- Existing overlap: Medium–High (P5, P8)
- Novelty potential: **LOW**
- Technical feasibility: High
- Required experiment: same as C
- Measurable metrics: same as C
- Main risk: same as C
- Recommendation: fold into E; not viable standalone

**E. Latency-aware adaptive QKD-PQC security for EHR sharing**
- Existing overlap: Low — this specific combination (EHR application +
  QKD-availability-adaptive fallback + latency as a core metric) was not
  found. Adjacent pieces exist separately (P1/P2/P3 static healthcare
  QKD+PQC; P5/P8 adaptive fallback for other domains).
- Novelty potential: **MEDIUM** (kept conservative rather than HIGH,
  given the search wasn't exhaustive and IEEE JBHI's open special issue
  on this exact intersection signals competing work may already be in
  submission)
- Technical feasibility: High — matches the existing tooling plan
  (Qiskit Aer, liboqs, Synthea synthetic EHR data)
- Required experiment: simulate an EHR transaction workload (routine
  vs. simulated emergency access) over a 6G-edge topology with a hybrid
  QKD-PQC key-establishment layer; inject QKD unavailability/degradation
  events; compare static-hybrid vs. adaptive-fallback across baselines
- Measurable metrics: key establishment latency, end-to-end EHR
  transmission latency, fallback rate, successful-transmission rate
  under QKD outage, communication overhead, throughput, scalability with
  device/user count
- Main risk: if the "6G" and "EHR" framing are cosmetic labels over P8's
  methodology, it reads as a domain swap — the EHR workload model and
  6G/edge topology need to do real work, not just relabel generic traffic
  as "medical data"
- Recommendation: **selected as the core direction** (Section 3),
  conditional on the EHR/6G specifics being substantive, not cosmetic

**F. Resource-aware QKD-PQC security for constrained IoMT devices**
- Existing overlap: Medium — P11 (PQC-only wearable resource
  benchmarking: NewHope, Kyber, XMSS) and a multi-domain QKD+PQC testbed
  found this session showing PQC/SDN overhead stays low on constrained
  devices while QKD key-retrieval is the actual bottleneck
- Novelty potential: **MEDIUM**
- Technical feasibility: Medium — QKD hardware physically doesn't fit on
  a wearable; a realistic framing needs QKD at the edge/gateway and PQC
  at the device, which changes this from "QKD on IoMT" to "QKD-PQC split
  across the edge-device boundary"
- Required experiment: benchmark PQC compute/memory/power cost on
  simulated constrained-device profiles, combined with an edge-side
  QKD-PQC hybrid link
- Measurable metrics: CPU/memory/power at device, key establishment
  latency, overhead
- Main risk: overlaps meaningfully with P11 unless the edge/device split
  and the EHR data path are both explicit
- Recommendation: viable as a **sub-contribution nested inside E**, not a
  strong standalone direction

**G. Multi-objective optimization of security, latency, and
communication overhead**
- Existing overlap: Low — no paper found does a systematic
  multi-objective/Pareto-style characterization of the QKD-PQC hybrid
  trade-off space in any domain; existing work reports point comparisons
  at fixed configurations
- Novelty potential: **MEDIUM** (not HIGH — trade-off characterization is
  a well-established *pattern* in security evaluation generally; the gap
  is in applying it here systematically, not in the concept itself)
- Technical feasibility: High — this is an evaluation-design choice
  (sweep multiple parameters, report the resulting surface) layered on
  top of whatever architecture is built, not new infrastructure
- Required experiment: sweep QKD availability × payload size × device
  count (× optionally PQC algorithm choice); report the resulting
  latency/overhead/security-level surface jointly rather than as isolated
  point comparisons
- Measurable metrics: the same set as E, analyzed jointly
- Main risk: without an underlying application (i.e., without being
  paired with an architecture), this is a method with nothing to apply it
  to — the issue isn't "already solved," it's "not yet meaningful as a
  standalone healthcare/6G claim"
- Recommendation: adopt as the **evaluation methodology inside E**, not
  as a separate direction

---

## 3. Selected core research problem

**Direction E**, using **Direction G's multi-objective evaluation lens**
as its methodology (not treated as a separate contribution — folding it
in is what keeps E from being a bare domain-swap of P8).

Why E over the alternatives:
- **Lowest existing overlap** of all seven directions per the collision
  table — the specific triple (EHR workload + QKD-availability-adaptive
  fallback + latency as a core, not incidental, metric) wasn't found.
- **Technically meaningful**: it tests whether a mechanism proven
  elsewhere (P5, P8) actually holds up under a workload and topology
  (EHR transactions, 6G-edge) it has never been tested against — a real
  empirical question, not a relabeling exercise.
- **Measurable**: eight concrete metrics (Section 7).
- **Supported, not contradicted, by literature**: P5/P8 show the
  mechanism is real and quantifiable; P1/P2/P3 show QKD+PQC-for-
  healthcare is real and field-viable; nothing found combines them.
- **Not already solved**: per the collision table and A–G labels above.
- **Realistically simulatable** with the team's existing stack.
- **Feasible in 2–3 months** for two students — no new cryptographic
  primitives, no physical QKD hardware.
- **Relevant to EHR** by construction (EHR is the workload).
- **Connected to 6G** through the edge topology and multi-site/device
  scalability axis, which is where 6G's expected ultra-dense,
  low-latency edge deployment model is actually load-bearing to the
  experiment design — not just a label.
- **Quantitative** across all eight metrics.

Directions A–D and F were ruled out or demoted above for concrete,
cited reasons, not by elimination alone.

---

## 4. Final research question

*The example question given in the task ("How does adaptive QKD-PQC key
establishment affect the latency, communication overhead, and resilience
of EHR sharing under varying QKD availability in 6G-enabled healthcare
networks?") is close to what the literature supports — but it omits the
scalability/device-count axis and the multi-objective framing that
differentiates this from a bare P8 domain-swap, so it's refined below
rather than used as-is.*

**RQ:** How does an adaptive QKD-PQC key-establishment mechanism — which
falls back toward PQC-only operation as simulated QKD availability
decreases — affect key-establishment latency, end-to-end EHR
transmission latency, communication overhead, and successful-transmission
rate, relative to classical, PQC-only, QKD-only, and static-hybrid
baselines, across varying QKD availability levels and simulated device/
user counts in a 6G-edge healthcare network topology?

---

## 5. Hypotheses

**H1 (availability/resilience):** Under full QKD availability, the
adaptive mechanism will achieve a successful-transmission rate close to
the QKD-only baseline; as simulated QKD availability decreases, it will
degrade gracefully toward PQC-only-level performance, while the
static-hybrid baseline will show a sharper drop (blocking or exposing a
weaker mode) at the same availability levels.

**H2 (EHR-specific cost, the axis P8 doesn't test):** The latency and
overhead cost of adaptive switching, relative to static hybrid, will
remain within thresholds acceptable for routine EHR access, but may
exceed acceptable bounds for a simulated emergency-access latency budget
specifically — a distinction that has no counterpart in P8's power-grid
traffic classes and is the concrete test of whether this is a genuine
domain contribution or a relabeling.

**H3 (scalability):** Fallback frequency and its associated overhead will
scale with simulated concurrent device/user count in a pattern broadly
consistent with P8's general findings, but the specific thresholds at
which healthcare-acceptable latency is exceeded will differ numerically
from P8's power-grid thresholds, reflecting different traffic and
criticality profiles.

---

## 6. Final contributions (exactly 3)

**C1 — Adaptive QKD-PQC key-establishment architecture for EHR sharing
in a simulated 6G-edge topology**, switching between QKD-only, hybrid,
and PQC-only modes based on simulated QKD channel availability.
- Classification: **ARCHITECTURAL** / **INTEGRATION** (combines proven
  pieces — P5's fail-safe layering concept, P1–P3's healthcare
  application, P8's fallback-fraction modeling — into a domain
  combination not previously evaluated; not a new cryptographic
  primitive)
- Evidence required: a working simulation showing mode transitions occur
  correctly and preserve at-least-one-primitive-secure composability
  (citing, not re-deriving, the composable-security framing already
  established in the hybrid QKD-PQC literature)

**C2 — Multi-metric evaluation against four baselines under varying QKD
availability and device count, on a synthetic EHR workload.**
- Classification: **EXPERIMENTAL** / **EXTENSION** (extends P8's
  evaluation methodology — SLA/availability comparison across baseline
  configurations — into a new application domain and workload model,
  using Direction G's multi-objective lens rather than single-point
  comparisons)
- Evidence required: full results across the defined variable sweep,
  with all baselines run under identical simulated conditions

**C3 — Characterization of where healthcare-relevant latency budgets
(routine vs. simulated emergency access) are and are not preserved under
degraded QKD availability, compared numerically against the
general-infrastructure thresholds reported in P8.**
- Classification: **ANALYTICAL** / **POTENTIALLY NOVEL** — flagged
  "potentially" because this is an absence-based claim (nothing found
  does this domain comparison), which is inherently provisional pending
  the full Task 3 systematic search
- Evidence required: explicit, literature- or workflow-justified latency
  thresholds (not invented ad hoc), and a direct numeric comparison
  against P8's reported thresholds — with an explicit note if the
  traffic models turn out not to be comparable enough to compare at all

No "first-ever" / "novel" / "unique" language is used above without a
cited basis; C1 and C2 are explicitly framed as integration/extension.

---

## 7. Experimental design implication

**Baselines:**
1. Classical cryptography (RSA/ECC)
2. PQC-only (e.g., ML-KEM + ML-DSA/SLH-DSA)
3. QKD-only
4. Static hybrid QKD-PQC (no fallback logic)
5. Proposed adaptive approach

**Controlled variables** (held fixed within a given comparison run, to
isolate the effect under study):
- PQC algorithm choice (fixed to one primary combination unless running
  a dedicated algorithm-comparison sub-experiment)
- Simulated hardware/compute profile
- Network topology (fixed edge-gateway-hospital structure)
- Target security level (e.g., NIST PQC security category)

**Varied (independent) variables:**
- QKD availability / injected outage rate — primary independent variable
  for the adaptive mechanism
- Number of concurrent simulated users/devices — scalability axis
- EHR payload size — routine text record vs. larger record with
  attachments
- Network congestion/latency conditions — nominal vs. degraded

**Metrics:**
- Key establishment latency
- End-to-end EHR transmission latency
- Throughput
- Communication overhead
- CPU/memory cost
- Fallback rate
- Successful transmission rate
- Scalability (metric degradation vs. device/user count)

---

## 8. Threat model

**In scope:**
- Quantum-capable adversary performing "harvest now, decrypt later"
  against classical/RSA-ECC components
- Passive interception of classical and quantum channels
- Man-in-the-middle on the classical authentication channel (relevant
  given P6's finding that the QKD classical channel itself needs PQC
  authentication)
- Compromised/malicious IoMT endpoint attempting to inject false records
  or interfere with fallback logic
- QKD channel unavailability (fiber disruption, key-rate exhaustion,
  adverse conditions) — modeled as a fault/threat condition, not merely
  an operational nuisance
- Downgrade/fallback attacks, where an adversary deliberately induces or
  spoofs QKD unavailability to force weaker PQC-only or classical
  operation

**Explicitly NOT claimed to be defended against:**
- Physical-layer QKD attacks (e.g., detector side-channel/blinding) —
  outside what a simulation study can meaningfully model
- Compromise of the underlying PQC hardness assumption — treated as an
  accepted external risk
- Insider threats using legitimate credentials
- Classical network/OS-level compromise outside the modeled
  key-establishment and transport layers

---

## 9. Scope — explicitly NOT attempted

- Physical QKD hardware development
- Complete 6G standardization
- Clinical outcomes
- Real hospital deployment
- Quantum computer implementation
- Universal healthcare cybersecurity
- Side-channel/physical-layer QKD security proofs
- Formal regulatory/compliance certification (HIPAA/GDPR) — motivating
  context only, not a compliance claim

---

## 10. Title decision

**NARROW** — not KEEP, not full REPLACE. The technology list in the
original title is accurate but doesn't reflect the actual contribution
(adaptive fallback behavior under degraded QKD availability); it needs
narrowing to foreground that, not replacing wholesale.

Three precise alternatives:

1. *Latency-Aware Adaptive QKD-PQC Key Establishment for Electronic
   Health Record Sharing in 6G-Edge Healthcare Networks: A
   Simulation-Based Evaluation Under Varying QKD Availability*
2. *QKD-Availability-Aware Hybrid Key Management for EHR Sharing at the
   6G Healthcare Edge: Fallback Behavior, Latency, and Overhead
   Characterization*
3. *Graceful Degradation in Hybrid QKD-PQC Security for 6G-Enabled EHR
   Sharing: A Multi-Metric Simulation Study*

---

## 11. Final research blueprint

**FINAL PROBLEM:**
Hybrid QKD-PQC security for healthcare data is real and increasingly
field-validated (2025–2026), and adaptive, availability-aware fallback
between QKD, hybrid, and PQC-only modes is separately real and validated
for other critical infrastructure (power-grid communications). No
verified paper combines the two: nobody has evaluated how an
availability-aware fallback mechanism behaves when applied to EHR
sharing traffic at a 6G-edge healthcare topology, where routine and
time-critical (emergency) access have different latency tolerances than
the power-grid traffic classes the mechanism has been tested against so
far.

**RESEARCH QUESTION:**
How does an adaptive QKD-PQC key-establishment mechanism — falling back
toward PQC-only operation as simulated QKD availability decreases —
affect key-establishment latency, end-to-end EHR transmission latency,
communication overhead, and successful-transmission rate, relative to
classical, PQC-only, QKD-only, and static-hybrid baselines, across
varying QKD availability levels and device/user counts in a 6G-edge
healthcare network topology?

**HYPOTHESIS:**
H1: The adaptive mechanism degrades gracefully (QKD-only-level
performance → PQC-only-level performance) as QKD availability decreases,
outperforming static hybrid on successful-transmission rate under
partial unavailability.
H2: Adaptive-switching latency/overhead cost stays within acceptable
bounds for routine EHR access but may exceed bounds for simulated
emergency-access latency budgets specifically.
H3: Fallback frequency scales with device/user count in a pattern
broadly consistent with prior critical-infrastructure findings, but
numeric thresholds differ from the power-grid case.

**OBJECTIVES:**
1. Implement the five baselines (classical, PQC-only, QKD-only, static
   hybrid, adaptive) in simulation.
2. Design a synthetic EHR workload with at least two access-criticality
   classes (routine, simulated emergency).
3. Inject QKD availability/outage conditions and measure fallback
   behavior across all baselines.
4. Sweep device/user count and payload size to test scalability.
5. Characterize the resulting multi-metric trade-off surface and compare
   thresholds against P8's power-grid findings.

**CONTRIBUTIONS:**
1. (ARCHITECTURAL/INTEGRATION) Adaptive QKD-PQC key-establishment
   architecture for EHR sharing in a simulated 6G-edge topology.
2. (EXPERIMENTAL/EXTENSION) Multi-metric evaluation against four
   baselines under varying QKD availability and device count on a
   synthetic EHR workload.
3. (ANALYTICAL/POTENTIALLY NOVEL) Characterization of where
   healthcare-relevant latency budgets are/aren't preserved under
   degraded QKD availability, compared numerically against
   general-infrastructure thresholds from prior work.

**BASELINES:**
Classical (RSA/ECC); PQC-only; QKD-only; static hybrid QKD-PQC;
proposed adaptive approach.

**METRICS:**
Key establishment latency; end-to-end EHR transmission latency;
throughput; communication overhead; CPU/memory cost; fallback rate;
successful transmission rate; scalability.

**THREAT MODEL:**
Quantum-capable adversary (harvest-now-decrypt-later), passive
interception, MITM on the classical/authentication channel, compromised
IoMT endpoint, QKD unavailability treated as an adversarial/fault
condition, downgrade/fallback attacks. Explicitly excludes physical-layer
QKD attacks, PQC hardness-assumption compromise, insider threats, and
out-of-model network/OS compromise.

**EXPECTED RESULT:**
Based on the pattern already established for a different domain (P8),
it is plausible that the adaptive approach will show measurably better
availability/successful-transmission behavior than static hybrid or
QKD-only under partial QKD outage, at some latency/overhead cost
relative to static hybrid. Whether that cost is acceptable for
routine vs. emergency EHR access, and where the numeric thresholds fall
relative to P8's power-grid results, is exactly what the experiment is
designed to determine — not assumed in advance. No specific numeric
result is claimed here.

**FINAL TITLE:**
*Latency-Aware Adaptive QKD-PQC Key Establishment for Electronic Health
Record Sharing in 6G-Edge Healthcare Networks: A Simulation-Based
Evaluation Under Varying QKD Availability*

**NOVELTY CLAIM:**
We integrate an availability-aware QKD-PQC fallback mechanism, previously
evaluated only for non-healthcare critical infrastructure, with a
synthetic EHR workload and 6G-edge topology, and characterize — via
simulation, not claimed as exhaustively unprecedented — the resulting
latency, overhead, and resilience trade-offs, which no verified paper
found in this search evaluates for this combination.

TASK 5 COMPLETE — READY FOR RESEARCH DESIGN.
