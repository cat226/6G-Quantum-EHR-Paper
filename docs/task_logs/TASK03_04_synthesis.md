# TASKS 3 & 4 — LITERATURE SYNTHESIS (FIRST VERIFIED BATCH)

**Project:** 6G-Enabled Hybrid Quantum-Secure Architecture for Electronic Health
Record Sharing
**Authors:** Ramana Sree K V, Verona Ann Mariya
**Status:** Real, search-verified literature collection has started. This is
**20 papers**, not the full 30–50 target. Coverage below is honest about which
topics are well-covered and which still need dedicated search passes.

---

## 0. What changed and why this batch exists

The previous attempt at Tasks 3–4 was correctly blocked: that session had no
web search tool and no network route to any bibliographic database, so it
stopped rather than recall papers from memory and label them "verified."

This session has `web_search` and `web_fetch` available. That unblocks Option
1 from the prior report. It does **not** mean a "verified literature evidence
package" was supplied to me this turn — I checked, and it wasn't (see the
note at the end of this doc). What follows is real, freshly-searched
literature, verified to varying degrees documented per-paper in
`literature_matrix.csv`'s `Verified` column. Nothing here was recalled from
training data and labeled verified.

**Verification levels used** (see matrix `Verified` column):
- `Y-full-text-fetched` — I fetched and read the actual paper/page.
- `Y-abstract-and-search-metadata-verified` — title/authors/year/venue/DOI
  confirmed via structured search-result metadata (not full text).
- `PARTIAL-...` — found via a citation in another paper's reference list, or
  via a search snippet only. Bibliographic core (title, venue, approximate
  year) is plausible but **not independently confirmed** — flagged for a
  direct fetch before it's relied on for a specific quantitative claim.

Per Task 3's own rule: nothing marked `PARTIAL` or `UNVERIFIED` is treated
below as an established fact. It's cited only for what it's actually
confirmed to be (a real, findable title at a plausible venue), not for
unconfirmed detail.

---

## 1. Coverage against your Section A.2 topics

| Topic | Coverage this batch |
|---|---|
| A. QKD | Reasonable — distance/trusted-node constraints (P14, P15, P20), routing (P13) |
| B. PQC | Reasonable — healthcare (P02, P05), 6G (P10, P16–P18) |
| C. Hybrid QKD-PQC | **Thin** — P04 and P12 are the only hybrid-plus-healthcare/6G candidates, and both are `PARTIAL`, unverified beyond snippet |
| D. 6G security architectures | Reasonable — P10, P11 (context only), P16–P19 |
| E. 6G healthcare/medical comms | **Strong single anchor** — P01 (fully verified) |
| F. EHR security | Weak — P03, P07 (both `PARTIAL`) |
| G. Medical IoT/IoMT security | Reasonable — P05, P06, P08, P09 |
| H. Edge-assisted healthcare security | Thin — P08 only |
| I. Quantum-safe networking | Reasonable — P13, P14, P15 |
| J. Quantum key management | Thin — P20 only, `PARTIAL` |
| K. Quantum-resistant authentication | Covered indirectly via P05, P09 |
| L. Low-latency secure comms | Covered via P01, P10 |

**Bottom line: Hybrid QKD-PQC + EHR/healthcare (topic C×F, the exact center
of your research question) is the thinnest-covered cell in the whole matrix**
— only P04, which is not yet independently verified. That is itself an
important, if provisional, signal (see Section 6).

---

## 2. QKD State of the Art (from verified evidence only)

- **Distance/deployment constraints (ESTABLISHED):** P14 is a real, recent
  (2026) field deployment demonstrating trusted-node QKD over 303 km on
  deployed fiber (270 km single-mode + 33 km multi-core), with coexisting
  classical traffic. P15 (IEEE ONDM 2023, snippet-verified) independently
  corroborates that long-haul QKD still depends on trusted-node placement,
  and that span-aggregation algorithms can extend inter-node distance by up
  to ~20%.
- **Trusted-node dependence as an open problem (ESTABLISHED as a stated open
  problem, not solved):** P13 (arXiv survey, preprint) and P20 (`PARTIAL`)
  both frame reducing reliance on trusted relays — via quantum repeaters or
  via PQC — as an unresolved research direction, not something already
  closed out.
- **Healthcare applicability:** No paper in this batch experimentally
  evaluates QKD directly against EHR or hospital traffic. P03 claims a QKD
  module inside a healthcare/blockchain framework but is unverified beyond a
  search snippet — flagged, not usable as established evidence yet.

**What's still conceptual vs. demonstrated:** the 303 km link (P14) is real
and experimentally demonstrated; anything about QKD *in a hospital or 6G
context specifically* in this batch is either absent or unverified.

## 3. PQC State of the Art (from verified evidence only)

- **Healthcare applicability (ESTABLISHED as a framing, not as deployed
  practice):** P02 (Frontiers in Health Services, fully metadata-verified)
  is the strongest anchor — it frames harvest-now-decrypt-later as the
  central healthcare risk and recommends PQC as the scalable
  enterprise-wide answer, with QKD reserved for specific backbone links
  rather than general use.
- **Constrained/IoMT devices:** P05 (systematic PRISMA review, MDPI
  *Computers*, metadata-verified) surveys 63 studies on PQC-based IoMT
  authentication specifically under resource constraints. P08 and P09
  (both `PARTIAL`, one an explicit preprint) point toward ML-KEM/Kyber as
  the practical choice for constrained medical devices, consistent with
  P02's framing, but neither is independently confirmed yet.
- **6G/network-level feasibility (ESTABLISHED, single strong source):** P10
  is a real, fetched primary source (not just metadata) benchmarking
  ML-KEM/ML-DSA/Falcon on open-source 5G/6G cores (Open5GS/Free5GC). It
  explicitly reports manageable computational overhead but real ciphertext
  and signature size expansion as the binding constraint at the network
  edge — this is a directly citable, evidence-grounded limitation for your
  Section 3.2.
- **No single "best" algorithm claim is supported by this evidence, and none
  is made here** — P10 itself declines to declare one PQC scheme
  universally optimal, consistent with the instruction not to do so.

## 4. Hybrid QKD-PQC State of the Art — CORE SECTION

This is the thinnest and most consequential section. Being honest about that
thinness matters more here than anywhere else in the matrix.

**What is confirmed to exist as a research direction:**
- P12 (`PARTIAL`, venue not yet confirmed as peer-reviewed/indexed) frames
  hybrid QKD+PQC as an answer to PQC's key-size/latency problem, and cites
  NGMN calling for adaptable hybrid architectures for 6G — but treats
  healthcare only as motivating context, not as an evaluated case.
- P11 is **not a paper** — it's an IEEE ComSoc Special Issue call-for-papers
  actively soliciting "hybrid classical-quantum cryptographic frameworks"
  and "quantum cryptography for edge and fog computing in 6G" as **open**
  topics. I'm keeping it in the matrix specifically because a live CFP
  asking for this work is itself weak evidence the community doesn't
  consider it already solved — but it is not evidence of a solution, and I
  have tiered it as N/A / non-paper rather than counting it as a finding.
- P10 explicitly states that combining ML-KEM with QKD "can support"
  long-term secure 6G but does **not implement or evaluate** that
  combination — it's named as future work, not delivered.

**What is claimed but not yet independently verified:**
- P04 (Blockchain in Healthcare Today) is the only source found so far that
  claims an actual QKD+PQC hybrid (QKD for key distribution, Dilithium at
  the blockchain consensus layer) applied specifically to telehealth/patient
  records. This is the single most important paper in the whole batch for
  your novelty question, and it is **not yet verified beyond a search
  snippet** — no confirmed author list, no confirmed DOI, no independently
  extracted quantitative results. **This must be fetched and read in full
  before Task 5.** If confirmed as described, it would be prior art
  directly on your combination (QKD + PQC + healthcare); if it turns out on
  full read to only gesture at both technologies without a real combined
  protocol (a known failure mode per your own Part 5, Q6), the novelty
  picture changes substantially in the other direction.

**Classification against your Part 3.3 categories A–G:** based on what's
confirmed so far, none of the seven hybrid-construction patterns (A–G) are
demonstrated as *both* healthcare-specific *and* independently verified in
this batch. P04 would plausibly fall under **C (QKD primary + PQC
authentication)** if confirmed. Nothing here is confirmed under B, D, E, F,
or G for the healthcare/6G case specifically.

## 5. 6G Security (from verified evidence only)

- **Research/proposed architectures (not standardization):** P01 (fully
  fetched) is a complete, real, peer-reviewed 6G-hospital security
  architecture — PQC (Kyber+Dilithium) + PUF hardware authentication + Zero
  Trust + blockchain audit + Shamir threshold cryptography — evaluated via
  discrete-event simulation with concrete numbers (48% detection-latency
  reduction, 68% false-positive reduction, 39% round-trip-latency
  improvement vs. RSA-AES baseline). This is squarely **research-proposed**,
  not standardized, and explicitly simulation-only (no real hospital
  deployment).
- **Current standardization vs. proposed:** none of the papers in this batch
  are standards documents in the ITU-R/3GPP/NIST sense — P11 is an IEEE
  ComSoc special-issue solicitation, not a standard. No 3GPP or ITU-R IMT-2030
  primary document was retrieved in this batch; that's a genuine coverage
  gap for your standards-priority tier (A.1, item 5) that needs a dedicated
  search pass.
- **Edge/cloud integration:** P10 evaluates PQC specifically at the network
  edge (bandwidth/ciphertext-expansion tradeoffs on constrained platforms).

## 6. Healthcare / EHR Security (from verified evidence only)

This is genuinely the weakest-covered topic in the batch, and that weakness
is itself informative rather than just a gap to apologize for.

- P02 (verified) explicitly separates *motivating* healthcare mentions from
  *evaluated* healthcare security work, and lands PQC — not QKD, not hybrid
  — as its practical recommendation for EHR-scale deployment.
- P03 and P07 both claim direct EHR-sharing relevance but are `PARTIAL` —
  unverified beyond a snippet. P07 in particular uses "quantum secure" in
  its title in a way that, per the source snippet, may actually describe
  generic quantum-*resistant* (i.e., PQC-style) mechanisms rather than QKD —
  this ambiguity is common in healthcare-adjacent security papers and is
  exactly the kind of thing Task 3's verification checklist (A.4) exists to
  catch. It is flagged, not resolved, here.
- **Question "is EHR transmission actually evaluated, or just motivating
  context?" — answer so far: mostly motivating context.** P01 evaluates
  *command transmission* in a hospital setting, not EHR record sharing
  specifically. No paper in this batch runs an experiment that transmits or
  processes actual EHR-shaped data end to end under a hybrid QKD-PQC
  scheme. That is a real, evidence-grounded observation for your gap
  analysis (Section 7 below), not an assumption.

## 7. Edge-Assisted Security (from verified evidence only)

Thin. P08 (`PARTIAL`, explicit preprint) and P10 (verified, fetched) are the
only direct sources. P10's finding that ciphertext/signature expansion binds
at the edge is the one solid, evidence-grounded technical constraint
available for this section right now.

## 8. Quantum-Safe Key Management (from verified evidence only)

- Rotation/revocation/interoperability with conventional infrastructure:
  **no paper in this batch directly addresses this.** This is a genuine,
  currently-empty cell — flagged rather than filled with a plausible-sounding
  but unsupported claim.
- Trust-model/distribution: P20 (`PARTIAL`) proposes a zero-trust multipath
  QKD key-distribution scheme addressing compromised-relay risk; P13
  corroborates trusted-node reduction as an open problem.

---

## Comparative Table (strongest verified/near-verified approaches only)

Built only from rows with `Y-*` verification or strong cross-citation
confirmation (P01, P02, P05, P10, P14, P19). Rows for `PARTIAL` papers are
intentionally omitted from a comparative table until confirmed — a
comparison table implies confidence the unverified rows don't yet earn.

| Approach | QKD | PQC | Hybrid | 6G | Healthcare | EHR | Edge | Auth | Latency Eval. | Comm. Overhead | Validation | Main Limitation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 – 6G Smart Hospital PQC Arch. | No | Yes | No | Yes | Yes | No | Yes | PUF+Dilithium | Yes (simulated) | Not primary focus | Discrete-event sim | No QKD; command-transmission not EHR-sharing focus |
| P02 – PQC-for-Healthcare Review | Mentioned only | Yes | No | No | Yes | Yes | No | N/A (review) | N/A | N/A | Review synthesis | No original architecture |
| P05 – PQC IoMT Auth. Review | No | Yes | No | No | Yes | No | No | Yes (survey) | N/A | N/A | PRISMA review | No original architecture |
| P10 – Quantum-Safe 6G Eval. | No | Yes | No (future work only) | Yes | No | No | Yes | N/A | Yes (TLS handshake) | Yes (ciphertext expansion) | Experimental benchmark | Not healthcare; preprint |
| P14 – 303km Trusted-Node QKD | Yes | No | No | No | No | No | No | N/A | N/A | N/A | Real field deployment | Preprint; not healthcare/6G |

**What this table shows plainly:** nothing in the *confirmed* evidence base
combines QKD + PQC + 6G + Healthcare + EHR in one evaluated system. The one
paper that might (P04) is unverified. That gap is real in the confirmed
evidence — but Section 9 below explains why it's a signal, not yet a
conclusion.

---

## Critical Analysis (answering only from the evidence above)

1. **Well established:** PQC (Kyber/Dilithium/ML-KEM) is computationally
   feasible on 6G-class infrastructure and constrained devices, with known,
   measured overhead (P01, P10). QKD trusted-node deployment over
   250–300+ km is real and field-demonstrated (P14, P15).
2. **Proposed repeatedly:** hybrid QKD+PQC as a general concept is proposed
   across multiple sources (P04, P12, P11-as-CFP) but rarely with a fully
   specified, independently-verified protocol for the healthcare case.
3. **Actually experimentally evaluated:** P01's architecture (simulated,
   not deployed) and P10's PQC benchmarks (real testbed) are the two
   strongest evaluated results in this batch.
4. **Purely conceptual:** the QKD+PQC+6G+healthcare combination as a whole
   — confirmed nowhere in this batch as an evaluated system.
5. **Which QKD-PQC combinations exist:** per confirmed evidence, none
   healthcare-specific. P04 claims one but is unverified.
6. **Truly hybrid vs. name-only:** cannot be answered yet for the one
   candidate (P04) that matters most — this is exactly why it needs a
   full-text fetch before Task 5.
7. **QKD unavailability handling:** not addressed by any paper in this
   batch (empty cell, honestly reported).
8. **Constrained IoMT devices:** yes, addressed by P05, P08, P09 (PQC side
   only, not hybrid).
9. **Latency measured:** yes — P01, P10.
10. **Communication overhead measured:** yes — P10 (ciphertext expansion).
11. **Scalability measured:** not directly in this batch; P13/P15 touch key
    rate and trusted-node count at the network-routing level only.
12. **EHR sharing actually evaluated:** no — see Section 6.
13. **6G actually modeled vs. mentioned:** modeled with real simulation in
    P01; modeled with real open-source 5G/6G cores in P10; mentioned only
    as context in several others (P02, P12).
14. **Edge computing implemented vs. proposed:** evaluated experimentally
    only in P10; proposed only in P08.
15. **Quantum-safe key management:** addressed only partially (P20, P13,
    both routing/trust-focused, not full lifecycle) — rotation and
    revocation specifically remain unaddressed in this batch.

---

## POTENTIAL GAP SIGNALS (not a declared research gap — for Task 5)

**Signal 1 — Hybrid QKD-PQC has essentially no *confirmed, verified*
healthcare/EHR-specific evaluated instance in this batch.**
- Supporting papers: absence across P01–P20; the one candidate (P04) is
  unverified.
- Evidence: comparative table above — no confirmed row has QKD=Yes,
  Hybrid=Yes, and Healthcare=Yes simultaneously.
- Why it may matter: this is close to the center of your proposed
  contribution.
- Confidence: **LOW-MEDIUM** — a real gap in *this batch's confirmed
  evidence*, not yet a claim about the literature as a whole (only 20 of a
  target 30–50 papers collected; P04 unresolved).
- Verification still needed: full-text fetch of P04; a dedicated search
  pass specifically for "QKD PQC hybrid EHR" and "QKD PQC hybrid hospital"
  phrasing variants; IEEE Xplore / ACM DL direct search if credentialed
  access becomes available (this session's web_search covers open web
  results, which skew toward MDPI/arXiv/preprint sources — paywalled IEEE/
  ACM primary literature is under-sampled so far, visible in how many rows
  are IEEE-secondary-citation-only).

**Signal 2 — The closest full-system neighbor (P01) is PQC-only, no QKD,
and focused on command transmission rather than EHR data sharing.**
- Supporting paper: P01 (fully verified).
- Evidence: explicit "Architectural Novelty" section in P01 claims novelty
  specifically *within the PQC-only, no-QKD design space* — it does not
  claim to be a hybrid QKD-PQC system.
- Why it may matter: if your proposed architecture is framed as "PQC for
  6G hospitals," P01 is prior art close enough to require explicit
  differentiation. If framed as "hybrid QKD-PQC for 6G *EHR sharing*"
  specifically, P01 does not cover the QKD or EHR-sharing dimensions.
- Confidence: **HIGH** (P01 is fully verified).
- Verification still needed: none for P01 itself; differentiation framing
  is a Task 5 decision, not a literature question.

**Signal 3 — "6G quantum-secure hybrid" is being actively solicited by IEEE
ComSoc as an open topic, not treated as closed.**
- Supporting evidence: P11 (CFP, not a paper — treated as context only).
- Why it may matter: weak corroborating signal that the community doesn't
  consider hybrid QKD-PQC-for-6G solved, consistent with Signal 1.
- Confidence: **LOW** (a CFP reflects editorial interest, not a literature
  gap in itself).

---

## Novelty Discipline (Candidate Contribution Classification)

| Candidate contribution element | Classification | Why |
|---|---|---|
| PQC (Kyber/Dilithium) for 6G healthcare command/data security | **KNOWN** | P01 already does this, evaluated, published 2026 |
| QKD for healthcare key distribution generally | **KNOWN** | P03 claims this (unverified detail, but the *concept* is not new — QKD-for-healthcare framing also appears in non-peer-reviewed sources found but excluded from the matrix, e.g. industry material from QNu Labs/ID Quantique) |
| Hybrid QKD+PQC combined key establishment, general (non-healthcare) | **KNOWN** | Confirmed via reference-list evidence across multiple 2023–2025 papers (P16–P19 lineage; P04's own apparent framing) |
| Hybrid QKD+PQC applied specifically to EHR sharing over 6G, evaluated | **UNCERTAIN — POTENTIALLY NOVEL** | No confirmed instance in this batch; P04 is the one unresolved candidate that could make this KNOWN or INTEGRATION instead |
| 6G-specific latency/edge evaluation of a hybrid QKD-PQC EHR architecture | **UNCERTAIN — leaning POTENTIALLY NOVEL** | P10 shows PQC-only 6G edge evaluation exists; nothing confirmed combines that with QKD and EHR simultaneously |

**Explicit flag per your Part 7 instruction:** if P04, once fetched in full,
turns out to be a genuine, evaluated QKD+PQC hybrid for healthcare records,
your architecture's novelty would need to shift from "hybrid QKD-PQC for
healthcare" (become INTEGRATION/EXTENSION relative to P04) toward whatever
specific dimension P04 doesn't cover — most plausibly the 6G-specific
latency/edge evaluation, or an EHR-sharing-specific protocol as opposed to
P04's telehealth/DAG-blockchain framing. **This is exactly the kind of
finding your own Part 7 instructions say should be surfaced, not
downplayed.**

---

## What this batch does NOT establish

- Not a claim that hybrid QKD-PQC-for-EHR is definitely unaddressed in the
  literature — only that it's unaddressed in *these 20 confirmed-or-flagged
  papers*, which skew toward open-web-indexed sources (arXiv, MDPI,
  Frontiers, Nature/Scientific Reports, PMC) rather than paywalled IEEE
  Xplore/ACM DL primary literature. Several IEEE papers appear here only as
  secondary citations (P15–P19) precisely because I couldn't always fetch
  IEEE Xplore pages directly — full text access there is more limited
  through this tool than through the open-web sources.
- Not a final tier/evidence assignment for P03, P04, P06, P07, P08, P09,
  P12, P13, P15–P20 — all `PARTIAL`, all need a direct fetch before being
  cited for a specific number or claim in the manuscript.
- Not Parts D–K fully worked (I've covered D, E, F, G, H, I, J, K, L above
  at the depth the 20-paper batch supports — some cells are thin by
  necessity, and I've said so rather than padding them).

## Suggested next steps (not proceeding without your direction, per Part 6/Task 5 boundary)

1. Fetch P04 in full — highest priority, directly affects your novelty claim.
2. Fetch P03, P06, P07, P12 in full to resolve `PARTIAL` status.
3. Run a dedicated search pass for standards documents (3GPP, ITU-R
   IMT-2030, ETSI GS QKD) — currently zero standards documents in the
   matrix, which is a real coverage gap against your own Section A.1
   priority list.
4. Continue toward the 30–50 target with additional searches specifically
   on: quantum-resistant authentication protocols (Topic K) and quantum key
   management lifecycle/rotation/revocation (Topic J) — both currently thin.

**TASKS 3 AND 4: FIRST VERIFIED BATCH COMPLETE (20/30–50 papers) — NOT YET
READY FOR TASK 5.** P04 needs full-text verification before the novelty
question in Section 9 can be answered with confidence either way.
