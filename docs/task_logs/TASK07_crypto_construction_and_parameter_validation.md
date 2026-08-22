# TASK 7 — Cryptographic Construction and Simulation Parameter Validation

**Project:** Latency-Aware Adaptive QKD-PQC Key Establishment for
Electronic Health Record Sharing in 6G-Edge Healthcare Networks
**Depends on:** Task 6 (approved, with 4 required modifications)
**Status:** Validation and specification only. No packages installed, no
code written, no experiments run, no numerical results fabricated.

## A capability note, stated plainly before anything else

This session does not have a live web-search tool available (same
constraint noted at the start of Tasks 3/4). Unlike that earlier point in
the project, this task is **not** fully blocked by that, because most of
what's needed here can be honestly answered from three sources: (1) the
already search-verified corpus you've fed back into this repo
(`literature_matrix.csv`, the Task 3/4/5 synthesis docs), (2) engineering
judgment applied to Task 6's own design, and (3) well-established,
extremely well-documented cryptographic standards (NIST FIPS 203/204,
RFC 5869, TLS 1.3 hybrid key exchange) that I have high confidence in
from training knowledge.

**Part 1 is the exception.** "Find and verify the strongest existing
published construction" is explicitly a literature-verification task,
and I do not have a way to run that verification live in this session.
What follows in Part 1 is the strongest defensible recommendation I can
make from existing evidence plus high-confidence general cryptographic
knowledge — every specific citation in it is labeled
**RECALLED-UNVERIFIED** and flagged as needing a dedicated
search-verification pass (the same kind of session that produced your
Task 3/4/5 material) before it can be treated as confirmed for the
manuscript. I want that distinction visible throughout, not buried in a
disclaimer at the top.

**Evidence labels used throughout this document** (extending Task 6's
scheme with one new label):
- **ESTABLISHED** — confirmed via a fully/near-fully verified source in
  your corpus (Clason et al. 2026; Devaraj et al. 2026), or a standard so
  widely documented that misremembering its core facts is very unlikely
  (NIST FIPS 203/204's existence and finalization status).
- **DESIGN ASSUMPTION** — grounded in a source found via live search but
  not yet full-text-verified in your corpus (Spooren et al. 2026; Zhu
  2025; Atutxa & Sanz et al. 2025).
- **RECALLED-UNVERIFIED** (new) — drawn from my training-data knowledge
  of cryptographic standards/literature, not confirmed via search this
  session or in your uploaded corpus. Treated as a strong working
  assumption for **implementation planning**, explicitly **not**
  sufficient to cite as fact in the manuscript without verification.
- **MODELED ASSUMPTION** — a simulation parameter we are choosing,
  not claiming to be a measured real-world fact.
- **SENSITIVITY VARIABLE** — a modeled assumption specifically flagged
  for later sensitivity testing because its value materially affects
  results and isn't well-anchored yet.

## Task 6 modifications — how they're applied throughout this document

1. **Criticality is now a secondary/optional analysis.** Part 4/7 below
   do not sweep it as an independent variable; the pilot generates a
   realistic routine/emergency mix but does not gate pilot success on a
   criticality-specific breakdown.
2. **No 450-cell commitment.** Part 7 designs a ≤30-configuration pilot
   with explicit, checkable criteria for any expansion.
3. **The hybrid KDF is verified, not implemented.** Part 1 recommends a
   construction and flags its citation-verification status; Part 9's
   implementation spec includes a `kdf.py` module *placeholder* in the
   directory structure but no code.
4. **6G stays an explicitly justified abstraction.** Part 5 keeps the
   current-tech vs. future-6G-target vs. simulation-simplification
   three-way split throughout, and restates the "not a finalized
   standard" caveat.

---

## PART 1 — Verify the Hybrid Key Construction

### Candidates considered

1. **Simple concatenation + unspecified KDF** (our Task 6 design):
   `KDF(QKD || ML-KEM || context)`. Functional, but "KDF" was left
   unspecified and `context` was concatenated directly into the input
   keying material rather than used as a KDF parameter — both are worth
   correcting, below.
2. **Concatenation combiner with a formally-analyzed KDF** — the
   general pattern: `K = KDF(secret_1 || secret_2)`, where `KDF` is a
   specific, well-studied construction (HKDF). **RECALLED-UNVERIFIED**:
   Bindel, Brendel, Fischlin, Goncalves & Stebila, *"Hybrid Key
   Encapsulation Mechanisms and Authenticated Key Exchange"* (PQCrypto
   2019) is, to my recollection, the paper that formally analyzes this
   combiner for hybrid KEMs, showing the combined key is secure if **at
   least one** of the two input KEMs is secure, under a KDF modeled as a
   strong extractor. This is exactly the property Task 6 Section 5
   assumed but did not prove.
3. **Cascade/nested combiner**: `K = KDF_2(secret_1, KDF_1(secret_2))`.
   **RECALLED-UNVERIFIED**: also treated in the same line of work as (2)
   as an alternative combiner with a similar security property. This
   pattern is, as best I can tell from the collision-table description
   in your uploaded corpus, close to what **Spooren et al. (2026)**'s
   layered WireGuard+Rosenpass-over-ETSI-QKD-API construction actually
   does in practice — Rosenpass produces a PQC-derived pre-shared key
   that gets mixed into WireGuard's own Noise-protocol handshake via a
   sequential KDF step, rather than a single flat concatenation.
   **DESIGN ASSUMPTION**, since Spooren et al. 2026 itself is not yet
   full-text-verified in your corpus (only known via the novelty
   collision analysis's collision table).
4. **Deployed industry precedent**: TLS 1.3 hybrid key exchange
   (**RECALLED-UNVERIFIED**, but I have high confidence this exists and
   is deployed at scale — Chrome and Cloudflare have run production
   hybrid PQC/classical TLS using an X25519+Kyber concatenation
   construction since roughly 2022–2023) uses exactly the concatenation
   pattern: `shared_secret = concat(classical_secret, pq_secret)`, fed
   into TLS's existing HKDF-based key schedule, with domain separation
   via the schedule's own label/context mechanism rather than raw
   concatenation of a session identifier into the secret material
   itself.
5. **Backing standard for the KDF choice**: NIST SP 800-56C Revision 2,
   *"Recommendation for Key-Derivation Methods in Key-Establishment
   Schemes"* (**RECALLED-UNVERIFIED**, high confidence this document
   exists in roughly this form) formally specifies extract-then-expand
   KDF methods (i.e., HKDF, RFC 5869) for deriving keying material from
   one or more shared secrets — the authoritative backing for using
   HKDF specifically, independent of which combiner topology (flat
   concatenation vs. cascade) is chosen.
6. **A QKD-inclusive precedent worth naming**: `draft-ietf-ipsecme-
   ikev2-multiple-ke` (**RECALLED-UNVERIFIED**, moderate confidence) is,
   to my recollection, an active IETF draft defining a generalized
   *N*-way KDF cascade for IKEv2 explicitly designed to be extensible to
   more than two key-exchange mechanisms — including, by design intent,
   inputs like QKD-supplied key material, not just classical+PQC. If
   confirmed, this would be the closest thing to a QKD-specific
   standardized combiner design, as opposed to (2)–(5) above, which
   formalize the general classical/PQC case and are being *extended*
   here to a third QKD input.

### Recommendation — replace the ad hoc construction

**Not a new combiner.** The recommended replacement is the
industry-standard pattern, made precise:

```
IKM  = QKD_key_material || ML-KEM_shared_secret
PRK  = HKDF-Extract(salt = session_salt, IKM = IKM)
session_key = HKDF-Expand(PRK, info = context_binding_label, L = key_length)
```

Two concrete corrections versus the Task 6 draft:
- **Name the KDF explicitly**: HKDF (RFC 5869 / NIST SP 800-56C Rev. 2),
  not a generic unnamed "KDF" — this is what makes the construction
  match an actual analyzed/deployed pattern rather than an ambiguous
  placeholder.
- **Move `context_binding` out of the raw input keying material and
  into HKDF's `info` parameter** (with an optional `session_salt` into
  `salt`). Concatenating context directly into IKM is a subtly different
  (and non-standard) construction from using it as `info`/`salt` — the
  standard usage (per the TLS 1.3 pattern and RFC 5869 itself) is
  `info`/`salt` for domain separation, IKM for actual secret material
  only. This is a correction toward the established pattern, not a
  design innovation.

### Answering the specific sub-questions

- **Exact construction**: concatenation combiner + HKDF, as above
  (primary recommendation). Cascade/nested HKDF (matching Spooren et
  al. 2026's apparent WireGuard+Rosenpass approach) is a viable
  alternative, particularly if implementation ends up building on a
  Rosenpass-style toolchain directly — flagged as an implementation-time
  choice between two established combiners, not an open research
  question.
- **KDF/combiner mechanism**: HKDF, extract-then-expand.
- **Security rationale**: per the (RECALLED-UNVERIFIED) Bindel et al.
  2019 line of work, a concatenation combiner with a strong KDF is
  secure if **at least one** input secret comes from a secure
  mechanism — directly matching the "at least one component remains
  secure" property Task 6 Section 5 assumed without proof.
- **Required assumptions**: HKDF behaves as a strong randomness
  extractor/PRF (the standard HKDF security assumption); the two input
  mechanisms fail independently — i.e., there's no single underlying
  cause that could break both QKD and ML-KEM at once. This independence
  assumption is worth stating explicitly as a **point in this
  combination's favor**: QKD's security rests on physics (no-cloning,
  photon detection), ML-KEM's on a math hardness assumption
  (Module-LWE) — these are about as independent as two security bases
  can be, which is a stronger independence argument than combining two
  *computational* mechanisms would give.
- **Authentication requirements**: the channel carrying the handshake
  transcript (our classical control channel, Task 6 Section 1/5) must
  be authenticated for the combiner's security argument to hold in
  practice — already satisfied by Task 6's ML-DSA-authenticated
  classical channel design.
- **Do both components need to be independently secure?** No — that is
  the entire point of using a combiner rather than requiring both.
- **Does it provide the claimed "at least one secure" property?** Per
  the RECALLED-UNVERIFIED Bindel et al. 2019 analysis, yes, **for the
  general 2-input KEM-combiner case**. Whether this extends cleanly to
  our specific 3-input case (QKD raw key material + ML-KEM shared secret
  + context label, where QKD's output is not itself a KEM but a
  raw-bits source) is a reasonable, standard restatement — but **not
  identical** to the proven theorem, and is flagged below (Go/No-Go
  Item 1) as the single most important open verification item carried
  out of this task.
- **Formally analyzed?** Yes for the general concatenation/cascade
  combiner pattern applied to two KEMs (RECALLED-UNVERIFIED citation).
  Not confirmed as formally analyzed specifically for a QKD-plus-KEM
  case in anything currently in your corpus or in what I can recall with
  confidence — this is a **DESIGN ASSUMPTION**, stated as such, not
  silently treated as equivalent to the proven case.
- **Suitable for simulation?** Yes — HKDF is fast, standard, and
  available in any crypto library already in `requirements.txt` (e.g.,
  `cryptography`'s `hkdf` module, or `pycryptodome`). No simulation-
  fidelity concern here, unlike the QKD physical-layer modeling
  question from Task 6.

---

## PART 2 — Verify Cryptographic Primitives

| Primitive | Standard/status | Security role | Parameter set | Computational/comm. characteristics | Implementation availability |
|---|---|---|---|---|---|
| **ML-KEM** | NIST FIPS 203 (2024), final standard — **ESTABLISHED** | IND-CCA2-secure KEM, Module-LWE hardness | **ML-KEM-768** (security category 3) recommended default | Public key/ciphertext on the order of ~1.1–1.2 KB each (**RECALLED-UNVERIFIED** exact byte counts — must be checked against the FIPS 203 spec directly at implementation time, not relied on from this recollection) | `liboqs` / `liboqs-python`, already in `requirements.txt` |
| **ML-DSA** | NIST FIPS 204 (2024), final standard — **ESTABLISHED** | EUF-CMA-secure signature, Module-LWE/Module-SIS hardness | **ML-DSA-65** (category 3, matches ML-KEM-768) | Signature size on the order of ~3.3 KB (**RECALLED-UNVERIFIED**, double-check against FIPS 204 at implementation time) | `liboqs` |
| **AEAD** | AES-256-GCM — **ESTABLISHED (standard technique)** | Confidentiality + integrity of the EHR payload | AES-256-GCM primary; ChaCha20-Poly1305 flagged as an alternative specifically for a future constrained-IoMT-device baseline (no hardware-AES assumption) — not committed to now | Hardware-accelerated on typical simulation hosts (AES-NI); available via `pycryptodome` or Python's `cryptography` package, both plausible per `requirements.txt` | Widely available |
| **Classical baseline (B1)** | X25519 (RFC 7748) for key exchange + Ed25519 (RFC 8032) for signatures — **ESTABLISHED (standard technique)** | Pre-quantum comparison point (Task 6 Section 11) | N/A — fixed, not swept | Small keys/signatures (32/64 bytes), fast — sets the "performance ceiling" baselines are compared against | `cryptography` package |

**No algorithm comparison performed**, per the instruction — one
parameter set per primitive (category 3 throughout) is chosen and fixed,
consistent with Task 6 Section 12's control-variable commitment. A
dedicated algorithm-comparison sub-experiment remains a flagged-but-not-
committed possibility, same as in Task 6.

---

## PART 3 — QKD Model Parameters

| Parameter | Value/range | Evidence type |
|---|---|---|
| Field-demonstrated distance/loss | 303 km trusted-node link (270 km single-mode + 33 km multi-core fiber); per-sub-link loss ~23 dB/110 km and ~36 dB/160 km | **MEASURED IN LITERATURE** — Clason et al. (2026), ESTABLISHED in your corpus |
| Qualitative rate-vs-distance behavior | Secret key rate decreases roughly exponentially with channel loss/distance (a standard QKD physical-layer property) | **RECALLED-UNVERIFIED** general knowledge — qualitative relationship only, no specific rate number relied upon |
| QKD key generation rate (nominal, for simulation) | TBD numeric value | **MODELED ASSUMPTION**, loosely anchored to the above but not copied from a specific paper's rate figure — set for simulation tractability (pool exhaustion should be rare at full availability, achievable under load) |
| QKD pool capacity | TBD (sized as "N sessions' worth" of key material at full charge) | **MODELED ASSUMPTION** — our own systems design (Task 6 Section 6), tied to per-session switching granularity |
| Key consumption per session | Determined internally by our own crypto design (Part 1/2 above — however many bits HKDF's IKM needs from the QKD side) | **Internally derived**, not an external literature parameter |
| Outage duration/pattern | Injected outage schedule (fixed-duration or stochastic on/off) | **MODELED ASSUMPTION** — the *approach* (stochastic availability modeling) is a DESIGN ASSUMPTION grounded in Zhu (2025)'s SLA/availability methodology per Task 5's blueprint; the *specific parameters* of that paper are not yet extracted into this corpus |
| Availability sweep levels | Task 6's 5-level set {100/75/50/25/0%}, reduced to a 3-point pilot set (Part 7) | **Experimental design choice**, not a literature-derived set of "real" availability figures — stated plainly, not implied to be measured |

**Explicitly not done**: no single experimental QKD result (e.g.,
Clason et al. 2026's specific link) is presented as representative of
"QKD deployments" generally — it is used only as a distance/loss
plausibility anchor, and the rate parameter itself remains a labeled
MODELED ASSUMPTION / **SENSITIVITY VARIABLE**, per the instruction not
to copy one result and generalize it.

---

## PART 4 — EHR Workload Parameters

Your own instruction anticipates this outcome directly: *"If literature
does not provide reliable payload distributions, define controlled
synthetic sizes and clearly label them as experimental assumptions."*
That is the situation here — nothing in the current corpus reports
specific FHIR-message byte-size statistics.

| Size class | Range | Basis | Evidence type |
|---|---|---|---|
| Small | ~1–5 KB | A single FHIR-style observation/vitals update or brief note is commonly in this range (general familiarity with FHIR resource sizes) | **RECALLED-UNVERIFIED / MODELED ASSUMPTION** — explicitly illustrative |
| Medium | ~20–80 KB | A visit-summary-style bundle (encounter + observations + conditions + medications) | **MODELED ASSUMPTION** |
| Large | ~200 KB – 1 MB | A composite bundle with attachments/imaging references or a lengthy document-style record | **MODELED ASSUMPTION** |
| Transaction frequency | TBD, set for tractability (routine device reporting on the order of once per minute to a few minutes; clinician-driven requests more sporadic) | Own modeling, loosely plausible, not literature-sourced | **MODELED ASSUMPTION** |
| Concurrent users/devices | {10, 100, 1000} full set (Task 6); {10, 1000} for the pilot (Part 7) | The independent scalability variable, not a fixed workload parameter | N/A — experimental design axis |

Generation method unchanged from Task 6 Section 10: procedurally
generated synthetic records, no real patient data, structure loosely
FHIR-inspired without claiming standard conformance.

---

## PART 5 — 6G-Edge Parameters

| Parameter | Current technology | Future 6G research assumption | Simulation simplification (what we actually model) |
|---|---|---|---|
| Access latency | 5G NR commonly-cited figures: ~4–10 ms typical, URLLC profiles targeting ~1 ms air-interface latency (**RECALLED-UNVERIFIED**) | ITU-R IMT-2030 vision reportedly targets sub-millisecond latency for certain use cases (**RECALLED-UNVERIFIED** specific figure; document's existence already used in Task 2/6) | Modeled as a configurable parameter set **between** current 5G/URLLC figures and 6G's more ambitious anticipated target — deliberately avoids both "just simulate today's 5G" and "assume 6G's most optimistic target as certain." **MODELED ASSUMPTION / SENSITIVITY VARIABLE** |
| Throughput | 5G peak rates commonly cited up to multi-Gbps in ideal conditions, realistically hundreds of Mbps typical (**RECALLED-UNVERIFIED**) | 6G research commonly discusses further multiplicative gains over 5G targets (**RECALLED-UNVERIFIED**, no specific figure relied upon) | Modeled at a level sufficient that EHR payload transmission time (Part 4) does not dominate end-to-end latency — a functional requirement on the parameter, not a copied figure |
| Packet loss | N/A (not the focus of a distance/frequency-specific claim) | N/A | Small nonzero baseline (nominal); elevated under the "congested" network-load level. **MODELED ASSUMPTION / SENSITIVITY VARIABLE** |
| Network load | N/A | N/A | Binary {nominal, congested} lever (Task 6 Section 13); pilot uses nominal only (Task 7 modification) |
| Edge processing delay | N/A | N/A | Mostly **not** a 6G assumption at all — it's dominated by our own *measured* PQC/AEAD operation timings (Part 2, real library calls per Task 6 Section 17), plus a small additional MODELED ASSUMPTION for non-crypto adaptive-decision compute overhead |
| Device population | 5G targets on the order of very high device density per km² are commonly cited (**RECALLED-UNVERIFIED**, no specific number relied on) | 6G research commonly discusses further increases over 5G's already-ambitious density targets (**RECALLED-UNVERIFIED**) | The device/user-count independent variable (Task 6 Section 12/13, reduced for the pilot per Part 4 above) — not a fixed parameter |

**Restated explicitly, per the instruction**: none of the above
represents a finalized 6G standard. The "future 6G research assumption"
column reflects anticipated targets from vision/framework documents, not
measured performance of any deployed system, and the simulation itself
sits in a deliberately-chosen middle ground, not at either extreme.

---

## PART 6 — Baseline Fairness (resolving Task 6's two open questions)

| | B1 — Classical | B2 — PQC-only | B3 — QKD-only | B4 — Static hybrid | B5 — Adaptive |
|---|---|---|---|---|---|
| **Authentication** | Ed25519 | ML-DSA-65 | **RESOLVED**: ML-DSA-65 authenticates the classical control channel (same mechanism as the proposed system) — "QKD-only" refers to the session-key *material* only, not the full authentication stack; stated explicitly to avoid ambiguity in the eventual paper | ML-DSA-65 | ML-DSA-65 |
| **Key establishment** | X25519 ECDH | ML-KEM-768 | QKD pool draw only | QKD pool draw + ML-KEM-768, always, combined via Part 1's HKDF construction | Task 6 Section 4 policy: either B2's or B4's key establishment, chosen per session |
| **Encryption** | AES-256-GCM keyed from ECDH secret | AES-256-GCM keyed from ML-KEM secret | AES-256-GCM keyed from QKD material | AES-256-GCM keyed from the combined secret | AES-256-GCM keyed from the mode-dependent derived key |
| **Failure behavior** | N/A | N/A (always available, software-only) | Blocks/fails when QKD unavailable — the unmitigated-outage comparison point | **RESOLVED**: blocks/fails when QKD unavailable, does **not** define its own fallback — this keeps B4 behaviorally distinct from B5 under outage, preserving its purpose as the adaptivity-isolating comparison | Falls back to B2's establishment path (Task 6 Section 4) |
| **Communication messages** | 1 RTT ECDH handshake + signature exchange; smallest message sizes | 1 RTT ML-KEM encapsulation + signature exchange; larger messages than B1 (PQC size overhead, Part 2) | QKD sifting/error-correction/privacy-amplification exchange (multiple protocol-internal rounds, modeled abstractly per Task 6 Section 17) + signature exchange for channel auth | B2's messages **and** B3's messages, concurrently, **plus** the HKDF combination step — highest message count of the five | Either B2-only or B4's full message set depending on the adaptive decision, **plus** the mode-sync handshake (Task 6 Section 3) in both cases — B5's overhead is therefore B2-or-B4's overhead plus a small, constant mode-sync cost |
| **QKD dependency** | None | None | Total | Required every session | Adaptive — required only in `MODE_HYBRID` |

**Fairness audit note**: all five baselines use the same AEAD
construction (AES-256-GCM), the same simulated topology/network
conditions, and the same EHR workload generator within a given cell —
restating Task 6 Section 11's commitment. Part 9's shared `Baseline`
interface (below) is the structural mechanism intended to enforce this
at the code level, but Task 6 Section 19.3 already flagged that this
still needs an explicit code-review-style check once implemented — not
assumed to be automatically satisfied just because a shared interface
exists.

---

## PART 7 — Reduced Pilot Experiment

### Exact pilot structure

| Axis | Pilot levels | Note |
|---|---|---|
| QKD availability | **{100%, 50%, 0%}** | Brackets both extremes plus one midpoint — enough to check the degradation trend is at least directionally plausible before committing to Task 6's full 5-point resolution |
| Device/user count | **{10, 1000}** | Brackets Task 6's 3-level range, dropping the middle (100) for the pilot |
| Payload | **medium only** | Per instruction — the representative "typical" case |
| Network load | **nominal only** | Per instruction — defers the congestion-robustness question |
| Criticality | Realistic routine/emergency mix generated as usual (Task 6 Section 10 default), but **not** a pilot success criterion (Task 6 modification #1) | Secondary/optional look only |
| Baselines | **All 5** (B1–B5) | Per instruction |

**Total pilot size**: 3 × 2 × 1 × 1 = **6 cells × 5 baselines = 30
configured runs** — exactly at the requested ceiling.

**Repetitions (pilot-specific)**: a small placeholder count (e.g., 5 per
cell) — explicitly provisional, since one purpose of the pilot itself is
to produce the variance estimate that sets the *full study's*
repetition count (Part 8).

### Purpose of the pilot
1. Validate the simulation harness and all 5 baselines run correctly
   end-to-end.
2. Produce a first-pass variance estimate (feeds Part 8).
3. Sanity-check that Task 6 Section 15's expected qualitative trends are
   at least directionally visible.
4. Surface Task 6 Section 19.3's flagged implementation risks (mode-sync
   bugs, fair-baseline violations, QKD pool-model realism) early and
   cheaply.

### Criteria for expanding to the full matrix

Expansion is justified only when **all** of the following hold —
explicit, checkable, not "if it looks good":

1. All 30 pilot runs complete without unhandled errors, across all 5
   baselines.
2. The fairness audit (Part 6) passes on the actual generated logs
   (message counts/overhead differ only where the design says they
   should).
3. B5 demonstrably switches modes in the logs at the 50% availability
   level — not just always defaulting to one mode (directly checks the
   Task 6 Section 19.3 "looks adaptive without being adaptive" risk).
4. **Consistency check**: B5 at 100% availability tracks close to B4 at
   100% (both effectively hybrid); B5 at 0% tracks close to B2 (both
   effectively PQC-only). If this doesn't hold, something is wrong with
   either the adaptive logic or baseline comparability, and must be
   fixed before expanding.
5. Observed variance is low enough that the planned condition
   differences (e.g., 100% vs. 0% availability) are distinguishable from
   noise at the pilot's small repetition count. If not, either the full
   study's repetition count needs raising, or an uncontrolled
   randomness source needs investigating first.
6. Pilot per-cell runtime is used to extrapolate full-matrix runtime
   (Task 6 Section 19.3's flagged risk). If the extrapolation exceeds
   what's feasible in the remaining timeline, the matrix itself — not
   just repetitions — may need further reduction.

**Only once all six hold** should the study expand — and even then, the
next step should be sized against the pilot's actual runtime data, not
automatically restored to Task 6's original 450-cell design. A
middle-ground expansion (e.g., 5 QKD levels × 3 device counts × 1–2
payloads × 1–2 loads) is a plausible next step; this decision is
explicitly deferred until the pilot's real data exists, not pre-decided
here.

---

## PART 8 — Statistical Plan

- **Repetitions**: **not** fixed to a round number now. Method: after
  the pilot, compute the pilot's observed variance (e.g., coefficient of
  variation) for the primary latency metric, then choose the full
  study's repetition count via a standard sample-size-for-target-CI-
  width calculation (e.g., targeting the 95% CI half-width within ~10%
  of the mean) — a statistically justified choice, not a habitual "run
  it 30 times."
- **Random seeds**: explicit, logged, documented sequence, per Task 6
  Section 18 — unchanged here.
- **Confidence intervals**: **95% CIs via bootstrap resampling**, not a
  normal-distribution assumption. Justification, specific to this
  design: latency distributions are expected to be right-skewed — a
  general property of networked/queueing latency data, sharpened here by
  a design-specific reason: Task 6 Section 4's decision logic includes a
  **bounded wait** for QKD replenishment under degraded availability,
  which by construction introduces a bimodal-ish or skewed latency
  shape (fast path vs. wait-then-fallback path) — exactly the situation
  a normal-assuming CI would misstate.
- **Median and mean, both reported**: mean for comparability with
  typical throughput/overhead reporting conventions; median because it's
  robust to the right-skew just described and better represents
  "typical" behavior under a skewed distribution.
- **95th-percentile latency**: retained from Task 6 Metric 1/2,
  justified as a general tail/worst-typical-case indicator even with
  criticality now a secondary axis (not swept) — the metric remains
  informative on its own.
- **Baseline-to-baseline comparisons**: default to a **Mann-Whitney U
  test** (non-parametric, two-sample), not a t-test — because latency
  data is expected to be non-normal/skewed for the reason above, and
  Mann-Whitney doesn't assume normality or equal variances. This default
  has an explicit escape hatch: if the pilot's actual data turns out
  reasonably normal on inspection (a real check to perform, not assumed
  either way), a t-test could be justified instead — the choice is
  data-driven, not doctrinal.
- **Multiple comparisons**: flagged for the eventual Results section —
  many pairwise baseline/condition comparisons will be made; a
  correction (Bonferroni, or a less conservative FDR method like
  Benjamini-Hochberg) should be applied once the actual number of
  comparisons is known, to avoid overstating findings from chance alone.

---

## PART 9 — Implementation Specification (structure only, no code)

```
experiments/
  src/
    baselines/
      baseline_interface.py   # abstract base class: establish_key(),
                               #   encrypt(), decrypt(), handle_failure()
                               #   — shared interface is the structural
                               #   mechanism enforcing Part 6 fairness
      b1_classical.py
      b2_pqc_only.py
      b3_qkd_only.py
      b4_static_hybrid.py
      b5_adaptive.py
    qkd_model/
      qkd_pool.py              # Task 6 Section 6 pool model
      qkd_availability.py      # outage/degradation injection (Part 3)
    pqc/
      ml_kem.py                # thin liboqs ML-KEM-768 wrapper
      ml_dsa.py                # thin liboqs ML-DSA-65 wrapper
    crypto/
      kdf.py                   # Part 1's HKDF construction — SPEC ONLY,
                                #   not implemented yet per instruction
      aead.py                  # AES-256-GCM wrapper
      classical_baseline.py    # X25519/Ed25519 wrapper for B1
    adaptive/
      controller.py            # Task 6 Section 4 decision logic
      mode_sync.py             # mode-sync handshake (Task 6 Section 3)
    workload/
      ehr_generator.py         # Part 4's synthetic EHR generator
      transaction.py           # size class, criticality flag, type
    network/
      sixg_model.py            # Part 5's latency/throughput/loss model
      topology.py               # Edge Gateway / Hospital Server / devices
    simulation/
      engine.py                 # SimPy-based discrete-event core
      scenario.py                # a single experiment cell's orchestration
    metrics/
      collector.py               # per-transaction event logging
      aggregator.py               # per-cell aggregation (mean/median/
                                   #   95th pct/CI, Part 8's methods)
    runner/
      experiment_runner.py        # reads configs, runs cells, invokes
                                   #   collector/aggregator; supports a
                                   #   pilot-only mode (Part 7)
      cli.py
  configs/
    pilot/                        # Part 7's 30 configs (or one
                                   #   parameterized template + generator)
    full_study/                   # populated later, pending Part 7's
                                   #   expansion criteria
    parameters.yaml                # Part 10's table, machine-readable,
                                    #   single source of truth
  results/
    pilot/{raw,aggregated}/
    full_study/{raw,aggregated}/   # populated later
  plots/
    pilot/
    full_study/
```

**Module notes** (interfaces, not implementations):
- `baseline_interface.py` defines the common contract all 5 baselines
  implement — the code-level fairness safeguard flagged in Part 6.
- `qkd_pool.py`: a `QKDPool` class with `level`, `capacity`,
  `generation_rate`, `debit(n_bits)`, `available_fraction()`.
- `controller.py`: implements Task 6 Section 4's `select_mode()`
  pseudocode as real code against a `QKDPool` instance and configured
  thresholds.
- `ehr_generator.py`: produces synthetic transactions per Part 4's size
  classes, parameterized from `parameters.yaml`.
- `experiment_runner.py`: config-driven orchestration; a `--pilot-only`
  flag runs just Part 7's subset without a separate code path.

**Result format**: raw per-transaction logs as JSON-lines (append-
friendly during long runs, directly loadable via `pandas.read_json
(lines=True)`, matching `requirements.txt`); aggregated per-cell
summaries as CSV (matches the existing `literature_matrix.csv`
convention in this repo — easy to inspect/diff in version control).

**Logging vs. metrics, kept separate**: a standard application log
(Python `logging`) for implementation diagnostics/errors is distinct
from the structured metrics event log (data for analysis) — conflating
"what happened, for analysis" with "what went wrong, for debugging" is
avoided deliberately.

**Plot generation**: one script per figure, reading only from aggregated
CSVs — never raw logs directly — keeping plotting fast and decoupled
from re-running the simulation, consistent with Task 6 Section 18.

**Reproducibility mechanism**: `experiment_runner.py` is the module
specifically responsible for enforcing Task 6 Section 18's checklist —
e.g., refusing to run a config without an explicit seed, auto-recording
an environment snapshot alongside each run's output.

**Nothing here is implemented.** This is directory/module/interface
structure only.

---

## PART 10 — Final Parameter Table

| Parameter | Value/range | Source | Evidence type | Justification | Sensitivity tested? | Final/temporary? |
|---|---|---|---|---|---|---|
| PQC KEM | ML-KEM-768 | NIST FIPS 203 | ESTABLISHED | Category-3 balance of security/constrained-device feasibility | No | Temporary |
| PQC signature | ML-DSA-65 | NIST FIPS 204 | ESTABLISHED | Matches ML-KEM-768's category | No | Temporary |
| AEAD | AES-256-GCM | Widely deployed standard | ESTABLISHED (standard technique) | Hardware-accelerated, well understood | No | Temporary (ChaCha20-Poly1305 flagged as IoMT alternative) |
| Classical KEX (B1) | X25519 | RFC 7748 | ESTABLISHED (standard technique) | Realistic modern pre-quantum baseline | N/A | Final |
| Classical signature (B1) | Ed25519 | RFC 8032 | ESTABLISHED (standard technique) | Pairs with X25519 | N/A | Final |
| Hybrid combiner | HKDF over concat(QKD, ML-KEM), context as `info`/`salt` | Bindel et al. 2019; TLS 1.3 hybrid KEX pattern; NIST SP 800-56C Rev. 2 (all RECALLED-UNVERIFIED) | DESIGN ASSUMPTION | Formally-analyzed ≥1-secure-component property; deployed pattern extended to a 3rd (QKD) input | No | **Temporary — highest-priority citation-verification item** |
| QKD nominal generation rate | TBD numeric value | Loosely anchored to Clason et al. 2026 (ESTABLISHED, distance/loss only) + general QKD scaling knowledge (RECALLED-UNVERIFIED) | MODELED ASSUMPTION | Tractability: rare exhaustion at full availability, achievable under load | **Yes — primary sensitivity variable** | Temporary |
| QKD pool capacity | TBD (N sessions' worth) | Own systems design | MODELED ASSUMPTION | Ties to per-session switching granularity | Yes | Temporary |
| QKD availability (pilot) | {100%, 50%, 0%} | Own experimental design | N/A | Brackets extremes + midpoint | N/A | Temporary — pilot-only |
| Device/user count (pilot) | {10, 1000} | Own experimental design | N/A | Brackets Task 6's 3-level range | N/A | Temporary — pilot-only |
| EHR payload — small | ~1–5 KB | General FHIR-size familiarity | MODELED ASSUMPTION | Single observation/vitals update | No | Temporary — illustrative |
| EHR payload — medium | ~20–80 KB | Same | MODELED ASSUMPTION | Visit-summary bundle | No | Temporary — illustrative |
| EHR payload — large | ~200 KB–1 MB | Same | MODELED ASSUMPTION | Composite bundle with attachments | No | Temporary — illustrative |
| Access latency (simulated) | TBD, bracketed | Between current 5G/URLLC figures and ITU-R IMT-2030 targets (both RECALLED-UNVERIFIED) | MODELED ASSUMPTION | Deliberate middle ground | **Yes** | Temporary |
| Network load levels | {nominal, congested} | Own design | N/A | Binary robustness check | Partial (pilot = nominal only) | Temporary |
| Packet loss (nominal/congested) | TBD pair | Own modeling | MODELED ASSUMPTION | Small baseline + elevated under congestion | **Yes** | Temporary |
| Repetitions per cell (pilot) | Small placeholder (e.g., 5) | Own design, pending pilot | N/A | Produces first variance estimate | N/A (this *is* the sensitivity step) | Temporary — pilot-only |
| Repetitions per cell (full study) | TBD, computed from pilot variance | Derived (Part 8's CI-width method) | N/A | Statistically justified, not arbitrary | N/A | Temporary — depends on pilot |
| Key rotation window (N txns / T sec) | TBD | Own systems design (Task 6 Section 6) | MODELED ASSUMPTION | Balances overhead vs. adaptivity responsiveness | **Yes** | Temporary |

This table is the canonical source of truth for implementation, per the
instruction — `configs/parameters.yaml` (Part 9) is its machine-readable
counterpart.

---

## PART 11 — Go/No-Go Check

1. **Is the hybrid key construction sufficiently justified?**
   **PARTIAL.** The construction pattern is well-established in general
   (RECALLED-UNVERIFIED citations) and matches deployed practice, but
   the specific citations are not confirmed this session, and the
   3-input QKD extension is a reasonable, not identical, restatement of
   the 2-input proof. **Safe to use for implementation planning; not
   safe to cite as verified fact in the manuscript yet.**

2. **Are ML-KEM/ML-DSA choices justified?** **YES**, with a minor
   caveat — FIPS 203/204 finalization is high-confidence established
   knowledge; exact byte-size figures cited should be spot-checked
   against the actual specs during implementation, but this doesn't
   block design-level readiness.

3. **Are QKD parameters defensible?** **PARTIAL.** Distance/loss
   grounding is real (Clason et al. 2026, ESTABLISHED); rate parameters
   are explicitly labeled MODELED ASSUMPTIONS / SENSITIVITY VARIABLES,
   which is the *correct* response to this evidence gap, not a blocker —
   but they are not yet literature-measured facts and must not be
   presented as such.

4. **Are EHR payload assumptions defensible?** **YES**, as explicitly
   labeled illustrative assumptions — which Part 4's own instruction
   permits when literature doesn't supply reliable figures. Not
   defensible as measured facts.

5. **Are 6G assumptions defensible?** **YES**, as explicitly-labeled
   simulation abstractions with a clear current/future/simplification
   split, consistent with Task 6 Section 9 and this task's modification
   #4.

6. **Are baselines fair?** **YES structurally** — both previously-open
   questions (B3 authentication, B4 failure behavior) are now resolved,
   and a shared code interface (Part 9) is the intended enforcement
   mechanism. Actual (implemented) fairness still needs the Task 6
   Section 19.3 code-review-style audit once code exists — design
   fairness and implementation fairness are different checks, and only
   the first is complete now.

7. **Is the pilot feasible?** **YES.** 30 runs at a small repetition
   count is a modest load, well within early-phase project timelines,
   using tooling already listed in `requirements.txt` (not yet
   installed).

8. **Are there remaining security assumptions that could invalidate the
   study?** **YES** — sharpened from Task 6 Section 19.2: specifically,
   if the concatenation combiner's formal security property does *not*
   actually extend cleanly to a 3-input QKD+PQC+context case (Item 1's
   flagged gap), the security claims in Task 6 Section 8 would need
   revisiting — and critically, the *performance* results could still
   look completely clean while resting on this unverified assumption.
   This is the single most important item carried forward.

9. **Is the design ready for implementation?** **YES, CONDITIONALLY.**
   Implementation may begin using the current best-available,
   explicitly-labeled choices, provided: (a) Item 1's citation gap is
   tracked as a must-resolve-before-manuscript-writing item, not
   forgotten once code exists; (b) the pilot actually runs and its
   expansion criteria (Part 7) are checked before scaling up; (c) the
   Part 10 parameter table is kept as the living source of truth, not
   silently drifted from as implementation reveals new information.

**Net assessment**: mostly GO. The one item that is "yes for
implementation, not yet yes for the paper" is the hybrid combiner's
exact citation — worth a dedicated, narrow search-verification pass
(a few targeted queries, not a broad sweep) before manuscript writing
begins, but not something that should block starting implementation.

---

**TASK 7 COMPLETE — IMPLEMENTATION MAY BEGIN ONLY AFTER REVIEW.**
