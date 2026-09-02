# TASK 5 — NOVELTY COLLISION ANALYSIS
**Project:** 6G-Enabled Hybrid Quantum-Secure Architecture for Electronic
Health Record Sharing
**Status:** Live-search verification pass complete (this session). **Not**
the full 30–50 paper systematic search specified in Task 3 — this is a
targeted collision check against the six claimed "closely related works"
plus adjacent literature discovered along the way. Every paper below was
found via live web search this session; none is recalled from training
memory. Full-text re-read (per the Task 3 checklist) has **not** been done
for all of them — flagged where that matters.

## A note on your six claimed items
None of your six items matched a single verifiable paper 1:1. What
actually exists is close in different ways to different items — closer
on some dimensions, absent on others. The real collision risk is not
"these six papers exist," it's that the *pairwise and triple
combinations* (QKD+PQC+healthcare, QKD+PQC+6G, PQC+EHR) are now each
independently covered by real 2025–2026 work, even though no single
paper found combines all five elements (6G + QKD + PQC + EHR + adaptive
fallback) at once.

Also relevant: **IEEE JBHI has an open Special Issue, "Quantum Key
Distribution for Secure Healthcare Information in 6G-Enabled Systems"
(submission deadline 31 Aug 2026)**, explicitly soliciting QKD-in-6G work
covering EHR, IoMT, and hybrid classical–quantum encryption. This special
issue explores the convergence of quantum communication and
next-generation wireless technologies to address growing security
challenges in digital healthcare, and focuses on integrating QKD into
6G-enabled healthcare infrastructure to secure EHR, imaging, remote
diagnostics, and IoMT. That doesn't mean the gap is closed — it means the
field has identified it as a live target, and there is likely competing
work already in submission that won't show up in an open search yet.

---

## Verified closely-related papers (collision table)

| # | Paper | System architecture | QKD role | PQC role | Key establishment | Key mgmt | Auth | EHR/data-sharing | 6G | IoMT/edge | QKD failure handling | Fallback | Adaptive | Latency eval | Overhead eval | Scalability | Method |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | Roosan et al. 2025, *PQC Resilience in Telehealth Using QKD*, Blockchain in Healthcare Today — integrates PQC with QKD and privacy-preserving mechanisms to protect patient records | DAG-blockchain + QKD + PQC + ZKP/MPC | Key exchange over quantum channel | Dilithium signatures at consensus layer | Hybrid QKD+PQC, not detailed | Blockchain-ledger based | ABE + smart contracts | Yes — patient records, telehealth | No | Edge-adjacent (clinics/devices) | Not addressed | Not addressed | No | Not primary metric | Yes (computational overhead) | Yes (DAG scalability) | Simulated network |
| P2 | Papadopoulos, Korakis, Balaskas 2026, *Practical Deployment of Hybrid QKD and PQC for Off-Site Hospital Data*, IEEE Access (Early Access) | Field pilot (HellasQCI/EuroQCI) | Real QKD link | Real PQC layer | Layered hybrid | Unclear — full text not read | Unclear | Yes — off-site hospital data | Not stated (fiber-based pilot) | Off-site/edge hospital link | Unverified — needs full-text check | Unverified | Unverified | Unverified | Unverified | Unverified | **Real field deployment**, not simulation |
| P3 | *Secure Medical Data Transmission Using QKD and PQC in Real-World Fiber Networks*, arXiv 2608.18869 (2026) | Trusted-node fiber network, 140 km | Entanglement-based QKD | End-to-end PQC authentication | Layered QKD+PQC | Not primary focus | PQC-based | Yes — rural health kiosk ↔ university hospital | No (fiber, not wireless 6G) | Yes — rural kiosk = edge node | Not the focus | Not addressed | No | Field-measured | Field-measured | Single link, not multi-node | **Real field deployment** |
| P5 | Spooren et al. 2026, *PQC-Enhanced QKD Networks: A Layered Approach*, IEEE QCNC 2026 | Layered WireGuard+Rosenpass over ETSI QKD API | Hop-wise pre-shared keys | End-to-end PQC key exchange (Rosenpass) | Dual-layer | Yes, explicit | Yes | No — generic multi-hop network | No | Trusted-node, not 6G | **Yes — explicit fail-safe design** | **Yes** | Partial | Yes (multi-hop) | Yes | Yes (multi-hop tested) | Lab testbed + simulation |
| P6 | Atutxa, Sanz et al. 2025, *Authentication of the QKD classical channel through PQC in a multi-site 5G/6G quantum-safe network* | Multi-site 5G/6G network | Classical-channel security | Authenticates QKD channel | PQC-authenticated QKD | Not central | **Yes — core contribution** | No | **Yes — explicit 5G/6G** | Multi-site | Not addressed | Not addressed | No | Not central | Not central | Multi-site | Real/testbed |
| P8 | Zhu 2025, *Techno-Economic Feasibility Analysis of QKD for Power-System Communications*, arXiv 2510.15248 | Power-grid comms (GOOSE/PMU traffic) | Compared vs PQC-only, Hybrid | Compared vs QKD-only, Hybrid | N/A (comparative study) | SLA/buffer-driven | Not focus | No — power systems, not healthcare | No | Long-haul/metro/distribution topologies | **Yes — stochastic modeling** | **Yes — explicit fallback fraction** | **Yes** | **Yes — core result** | Implicit | **Yes — core result** | Stochastic/statistical simulation |
| P10 | Mahesh & Mishra 2025, *PCBQC: Blockchain-Based Patient-Centric EHR using Hybrid PQC Lattice Algorithms*, Int J Performability Eng 21(11) | Blockchain + lattice PQC | None (no QKD) | Multiple lattice PQC algorithms combined ("hybrid" = PQC-only) | PQC-only | Patient-centric, explicit | Yes | **Yes — EHR is the subject** | No | No | N/A | N/A | N/A | Not central | Yes | Not stated | Not verified in depth |
| P11 | Maqsood, Hameed, Junaid, Tahir 2025, *Enhancing IoT Healthcare Security with PQC*, IEEE Xplore doc 10937815 | Wearable IoMT devices | None (no QKD) | Evaluates NewHope, Kyber, and XMSS for wearables | PQC-only | Not central | Not central | No — general medical records, not EHR workflow | No | **Yes — wearable IoMT, resource-constrained** | N/A | N/A | N/A | Yes | Yes (memory, power) | Not central | **Real hardware benchmarking** |

**Not fully verified (flagged, not entered above):** the IEEE Access
listing for P2 was confirmed via the author's own LinkedIn announcement
describing a resilient hybrid QKD–PQC architecture to protect sensitive
healthcare data and a citation from P3's reference list — not yet via
direct IEEE Xplore fetch. Full-text read (title/DOI/claims re-check per
the Task 3 checklist) is still owed before this enters the final
bibliography.

**Also identified, lower relevance (Tier 3–4, general context only):**
integration survey (Kalniņa, ACNS 2025 workshop, PQC+QKD applications/
challenges, no healthcare or 6G angle); IPsec hybrid QKD-PQC sequencing
study (Blanco-Romero et al. 2025); 6G quantum-safe survey mentioning EHR
in passing as one of several use cases where PQC can protect patient data
stored in electronic health records (Scifiniti 2025, not IEEE, not an
architecture paper); QKD+OTP (not PQC) medical-image transmission for IoT
telemedicine (Scientific Reports); a Qubitera Holdings PQC-only EHR
roadmap (industry press release, not peer-reviewed, no QKD).

---

## A–G evidence-discipline labels

| Claim | Label | Basis |
|---|---|---|
| A. Static QKD-PQC hybrid EHR security | **EXISTING** | P1, P2, P3 all combine QKD+PQC to protect hospital/patient data in a fixed (non-adaptive) architecture. Not literally "EHR record-sharing workflow" in the FHIR/HL7 sense — closer to "patient data in transit" — but the security-architecture claim is covered. |
| B. Adaptive QKD-PQC security | **PARTIALLY ADDRESSED** | Real for general/critical-infrastructure networks (P5, P8) — not verified for healthcare. |
| C. QKD failure-aware PQC fallback | **PARTIALLY ADDRESSED (general infra) / NOT FOUND (healthcare)** | P5 has explicit fail-safe design; P8 has explicit fallback-fraction modeling. Neither is healthcare-scoped. |
| D. Dynamic selection based on QKD availability | **PARTIALLY ADDRESSED (general infra) / NOT FOUND (healthcare)** | Same basis as C — P5/P8, plus secondary references to Makris 2024 and further Sanz 2025 work describing mode transition between QKD, hybrid, and PQC without data-path interruption, none healthcare-scoped. |
| E. Key-management optimization for EHR | **PARTIALLY ADDRESSED** | P10 does EHR-specific key/access management but with PQC only, no QKD. |
| F. Latency-aware hybrid security in 6G healthcare | **NOT FOUND** | No paper found combines 6G + latency-as-core-metric + hybrid QKD-PQC + healthcare. Closest single-axis matches: P6 (6G+QKD+PQC, not healthcare, not latency-focused) and P8 (latency/SLA-focused hybrid QKD-PQC, not 6G, not healthcare). |
| G. Security/performance tradeoffs under different QKD availability conditions | **EXISTING (general infra) / NOT FOUND (healthcare or 6G)** | P8 is a direct, rigorous instance of this evaluation methodology — for power-grid traffic, not EHR. |

**Important caveat on all "NOT FOUND" labels:** this reflects an
unexhaustive live search (~10 targeted queries), not the full 30–50 paper
systematic pass Task 3 specifies, and it cannot see papers currently
in submission to venues like the JBHI special issue above. "Not found"
here means "not found by this pass" — not "confirmed absent from the
literature."

---

## Candidate direction evaluation

**Direction 1 — Generic 6G+QKD+PQC+EHR architecture**
- Overlap: High. P1+P2+P3 cover QKD+PQC+healthcare; P6 covers QKD+PQC+6G. The generic combination is now assemblable from existing pieces.
- Novelty potential: Low as a bare architecture claim.
- Feasibility: High (well-trodden components).
- Risk of being incremental: **High** — reviewers who know P1/P2/P6 will read this as recombination.
- Recommendation: Do not pursue in this generic form.

**Direction 2 — Hybrid QKD-PQC EHR architecture (drop 6G)**
- Overlap: High, specifically against P1 and P2, which already do close to this.
- Novelty potential: Low–Moderate — would need a concrete EHR-workflow-level differentiator (e.g. FHIR-resource-level operations, not just "patient data").
- Feasibility: High.
- Risk of incremental: High.
- Recommendation: Not strong enough on its own.

**Direction 3 — Adaptive QKD-PQC key management (no healthcare scoping)**
- Overlap: Moderate–High against P5 and P8, which already do adaptive/fail-safe QKD-PQC switching for general and critical-infrastructure networks.
- Novelty potential: Low as stated — this is arguably the most mature sub-area found in this search.
- Feasibility: High.
- Risk of incremental: High.
- Recommendation: Not viable without a new application domain.

**Direction 4 — QKD-availability-aware PQC fallback (no healthcare scoping)**
- Same overlap profile as Direction 3 (P5, P8 cover this core idea for other domains).
- Novelty potential: Low as stated.
- Recommendation: Only viable as a *methodology transplant* into a new domain — see Direction 5.

**Direction 5 — Latency-aware adaptive QKD-PQC security for EHR sharing**
- Overlap: **Lowest of the six.** This is the one combination — EHR/healthcare application + adaptive QKD-availability fallback + latency-as-core-metric — that no single found paper covers. P8 proves the *methodology* (fallback fraction, SLA-availability comparison of Hybrid vs. QKD-only vs. PQC-only) works and is publishable, just not in healthcare. P1/P2/P3 prove QKD+PQC-for-healthcare is real and current but static.
- Novelty potential: **Moderate–High**, conditional. The risk: if the contribution is "P8's methodology, EHR data instead of power-grid data," that alone is thin — reviewers can call it a domain swap. The differentiator needs to be substantive: EHR-specific transaction semantics (e.g. read vs. write vs. emergency-access latency budgets), IoMT-device constraints P8 doesn't have, or a 6G-edge topology P8 doesn't model.
- Feasibility: High — matches your team's existing simulation stack (Qiskit Aer, liboqs, synthetic EHR data) and 2–3 month plan.
- Risk of incremental: Moderate, manageable with the above differentiators; High if left as a bare transplant.
- Recommendation: **Strongest candidate**, with the differentiation requirement stated explicitly rather than assumed.

**Direction 6 — Resource-aware QKD-PQC security for constrained IoMT devices**
- Overlap: Moderate. P11 does PQC-only resource evaluation on wearables (no QKD); P3/P4 involve edge nodes but not resource-constrained *device*-side QKD.
- Novelty potential: Moderate, but with a physical-plausibility problem: QKD requires specialized quantum hardware that a battery-constrained wearable realistically can't host — the honest framing is QKD-at-gateway + PQC-at-device, which is closer to Direction 5's edge topology than to literal "QKD on IoMT."
- Feasibility: Moderate (needs a defensible architecture where QKD lives at the edge/gateway, not the device).
- Risk of incremental: Moderate.
- Recommendation: Viable as a secondary framing or a scoped sub-contribution of Direction 5, not as a standalone direction.

---

## Recommendation

Based only on the verified literature above: **Direction 5** (latency-aware,
QKD-availability-adaptive hybrid QKD-PQC security for EHR sharing) is the
strongest candidate. It is the only direction where the specific
combination of elements wasn't found, it has a proven methodological
template to build on (P8) rather than starting from nothing, and it fits
your team's existing tooling and timeline. It is **not** a safe or
confirmed gap — it is the least-collided candidate in an
unexhaustive search, sitting in a topic area IEEE JBHI has just opened a
special issue for. Before locking a final title or contribution
statement, the individual papers above (especially P2, P5, P6, P8) need
the full Task 3 per-paper verification checklist run against their actual
IEEE Xplore / arXiv records, not just search snippets.

**NOVELTY COLLISION ANALYSIS COMPLETE — AWAITING REVIEW.**
