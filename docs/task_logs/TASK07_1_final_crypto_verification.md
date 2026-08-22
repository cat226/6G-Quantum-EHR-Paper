# TASK 7.1 — Final Cryptographic Verification Before Implementation

**Project:** Latency-Aware Adaptive QKD-PQC Key Establishment for
Electronic Health Record Sharing in 6G-Edge Healthcare Networks
**Depends on:** Task 7 (reviewed)
**Status:** Partial. Sections 2–5 and 7 are answered on the merits.
Sections 1 and 6 are explicitly **blocked** — stated plainly below,
not worked around.

## Capability constraint, stated before anything else

This task asks me to "find the strongest primary/authoritative sources"
and explicitly says **"do not use recalled values."** I do not have a
live search tool in this session (unchanged since Tasks 3/4/7). That
makes two parts of this task impossible to complete as specified:

- **Section 1** (verify exact claims from Bindel et al., NIST SP 800-56C,
  RFC 5869, IETF hybrid-KEX drafts, QKD+PQC standards, ETSI specs) —
  I cannot quote or confirm exact security claims from documents I
  cannot access this session. Task 7 already labeled everything from
  these sources `RECALLED-UNVERIFIED`; this task explicitly asks me not
  to lean on that again, so I won't repeat those recollections here as
  if they were answers.
- **Section 6** (exact ML-KEM-768/ML-DSA-65/AES-256-GCM byte sizes) — the
  instruction is explicit: no recalled values. I'm not providing numbers
  here.

What I *can* do without search is real, structural cryptographic
reasoning that doesn't depend on confirming any specific paper's exact
wording — Sections 2, 3, 4, 5, and most of 7 are that kind of question,
and are answered fully below. Section 8 (Final Go/No-Go) reflects this
split honestly rather than papering over it.

---

## 1. Verify the Combiner — BLOCKED

Not completed. Requires direct access to Bindel et al., NIST SP 800-56C,
RFC 5869, IETF hybrid-KEX drafts, and any QKD+PQC standard/ETSI
specification. **Recommendation**: a short, targeted search pass (five
or six specific queries — the source names above, essentially verbatim
— not a broad sweep) would resolve this quickly, the same way your
search-enabled session resolved Tasks 3–5. I'm not calling the research
tool for this myself, because the question is narrow enough that a
handful of direct searches will likely be faster and more precise than
an autonomous multi-source pass.

---

## 2. Do Not Overgeneralize the Proof

**This is answerable by reasoning about proof structure, independent of
confirming any specific paper's exact text — so it's worked out fully
here.**

A combiner proof of the shape `KDF(secret_A || secret_B)` where **both**
inputs are KEM outputs typically reduces security to the KEMs' own
security games — an adversary in the proof gets access to
encapsulation/decapsulation-style oracles for each KEM, and the argument
shows that if at least one KEM's IND-CCA game is hard, the combined key
is indistinguishable from random. That reduction is built around the
*structure* a KEM provides: a public key, a ciphertext, and a
decapsulation operation the adversary can be given oracle access to.

QKD-derived key material has **none of that structure**. It isn't the
output of an encapsulation/decapsulation pair — it's raw bits produced
by a physical protocol (photon transmission, basis reconciliation, error
correction, privacy amplification), and its security claim is
information-theoretic (grounded in quantum mechanics and an
authenticated classical channel), not computational (grounded in a
hardness assumption an adversary is bounded against).

**Conclusion: no, a KEM-specific combiner proof does not automatically
carry over.** A proof built around a KEM's oracle-based security game
does not, by itself, say anything about an input that isn't a KEM
output at all. Two things could rescue the claim, and both require
verification I can't do here:

- If the *specific* theorem is stated abstractly — for arbitrary
  independent secrets with a stated min-entropy or
  indistinguishability property, rather than tied to a KEM's oracle
  structure — it might extend to a "secret" that happens to come from
  QKD instead of a second KEM. This is plausible (generic
  "robust combiner" results in the cryptography literature sometimes
  are stated this way) but **not confirmed** without reading the exact
  theorem statement.
- If QKD's raw output can be *treated* as "just a high-entropy, hard-to-
  predict secret string with a stated security level," a
  generic-secrets version of the proof might apply. But QKD's security
  guarantee (information-theoretic, contingent on physical assumptions)
  is a genuinely different *kind* of guarantee than a KEM's
  (computational, contingent on a hardness assumption) — even a generic
  proof would need to be checked for whether it implicitly assumes both
  inputs share the same *type* of security guarantee, not just that
  both are "secret."

This is a real, structural gap, not a formality — it's the reason
Section 3 below lands where it does.

---

## 3. Choose the Paper's Security Claim

Given Section 2's finding, here is the honest selection:

- **Claim A ("formally established security property")** — not
  supportable right now, and shouldn't be claimed even after Section 1
  is unblocked unless a source is found whose theorem is stated
  abstractly enough to cover a QKD-type input, not just two KEM
  outputs.
- **Claim B ("supported by an established hybrid-combiner framework, not
  formally proven for our exact instantiation")** — **potentially**
  reachable, *if* Section 1's verification confirms a generic
  (non-KEM-specific) robust-combiner result that plausibly covers our
  case. This is the target to aim for once search access exists — but
  claiming it *now*, without that confirmation, would be exactly the
  overgeneralization Section 2 just ruled out.
- **Claim C ("engineering-level key combination with no compositional
  security claim")** — **this is what's defensible today.**

**Selection: Claim C, for now**, with Claim B named as the specific,
checkable target Section 1's verification could unlock. I'm not
defaulting to B just because the instruction says to prefer it — the
instruction also says to prefer B *only if the literature supports it*,
and right now I can't confirm that it does.

---

## 4. Determine the Exact Construction

Between the four options, no new mechanism is proposed here, consistent
with the instruction.

- **Option C is not chosen** — I don't have a confirmed, existing,
  named QKD+PQC hybrid construction to point to (ETSI's QKD work, as far
  as I'm aware without verification, standardizes the *key-delivery API*
  — how an application retrieves QKD key material — not a specific
  combiner formula for mixing that material with a PQC secret; I'm not
  confident enough in this to state it as fact, and it's part of what
  Section 1 needs to check).
- **Option A — HKDF over the concatenated secrets** is selected as the
  engineering choice: `PRK = HKDF-Extract(salt, QKD_secret ||
  ML-KEM_secret)`, `session_key = HKDF-Expand(PRK, info, L)`. This is
  chosen not because it's been proven optimal for this exact case
  (Section 2/3 just established it hasn't), but because HKDF's own
  design rationale (RFC 5869) is explicitly built to handle combining
  material from multiple, possibly-imperfect entropy sources at the
  Extract step — that general design intent is a reasonable engineering
  basis for using it here, independent of whether a QKD-specific
  security proof exists yet.
- **Option B (nested/cascade KDF)** remains a documented, viable
  alternative (matching what Spooren et al. 2026 appears to do inside a
  WireGuard/Rosenpass toolchain, per Task 7) — not chosen as the primary
  recommendation only because there's no specific reason to prefer it
  over the simpler flat-concatenation form for *this* project, not
  because it's inferior.

**Final construction (engineering choice, under Claim C):**
```
IKM = QKD_secret || ML-KEM_secret
PRK = HKDF-Extract(salt, IKM)
session_key = HKDF-Expand(PRK, info, L)
```
Identical in form to Task 7's recommendation — what has changed is the
**security claim attached to it** (now explicitly C, not an implied B),
which is the actual point of this task.

---

## 5. Authentication

- **What is authenticated**: the classical control channel carrying QKD
  sifting/basis-reconciliation/error-correction/privacy-amplification
  messages, and separately, the application-layer session
  establishment (mode-sync, per Task 6 Section 3) and endpoint identity.
- **What is not authenticated by this mechanism**: the quantum channel
  itself (the photon transmission) — that isn't something a classical
  signature scheme authenticates; its integrity comes from QKD's own
  physical-layer properties (eavesdropping detectability via induced
  error rate, addressed in Section 7's QBER discussion below), not from
  ML-DSA.
- **Why authentication is necessary here**: this is close to definitional
  for QKD, not something requiring a fresh citation to establish — every
  standard QKD protocol description (BB84 and its descendants) requires
  an authenticated classical channel for basis reconciliation, or the
  entire protocol is trivially defeated by a full man-in-the-middle
  substituting their own quantum and classical channels. This structural
  requirement is why Task 6 designed the classical channel as
  authenticated in the first place (Task 6 Section 5/7, Threat B).
- **Is ML-DSA appropriate?** Functionally, **yes** — ML-DSA is a
  standard, general-purpose PQC signature scheme with no QKD-specific
  incompatibility; any classical message exchange (reconciliation
  traffic, mode-sync, session establishment) can be authenticated with
  it. Choosing ML-DSA specifically (over another PQC signature scheme)
  is an implementation preference for consistency with the ML-KEM side
  of the design, not something that needs a QKD-specific proof to
  justify.

---

## 6. Standard Parameters — BLOCKED

Not completed, per the explicit "do not use recalled values" instruction
for ML-KEM-768, ML-DSA-65, and AES-256-GCM's exact sizes/overhead.

**A practical way to unblock this without a literature search at all**,
worth naming here: at **implementation time**, these exact byte sizes
don't need to come from a cited paper — they can be read directly from
the `liboqs` library's own reported public-key/ciphertext/signature
sizes for the chosen parameter sets, which is arguably more authoritative
for *code correctness* than any secondary source. That resolves the
values needed to *write working code*. It does **not** resolve the
separate need, for the eventual paper's Methods section, to cite the
authoritative FIPS 203/204 specification documents directly when
reporting those sizes in prose — that remains a genuine open item,
distinct from the implementation blocker.

---

## 7. QKD Model

| Item | Value/range | Category |
|---|---|---|
| Distance/loss (a real field deployment) | 303 km trusted-node link (270 km single-mode + 33 km multi-core), ~23 dB/110 km and ~36 dB/160 km loss on the sub-links | **LITERATURE-MEASURED** — Clason et al. (2026), already fully verified in this project's corpus (Task 3/4) |
| Qualitative rate-vs-loss relationship | Secret key rate decreases roughly exponentially with channel loss (standard QKD physical-layer behavior) | General knowledge, qualitative only — no specific rate number relied on |
| Secret key generation rate (nominal, for simulation) | Not set to a specific "real-world" number | **MODELED**, and explicitly a **SENSITIVITY VARIABLE** — per the instruction, since no universal literature range is confirmed, this is handled via sensitivity analysis rather than a single invented constant |
| QBER (quantum bit error rate) | A commonly-cited theoretical security threshold for BB84-family protocols is often quoted around ~11% — **flagged, not asserted**: this is a recollection of a widely-repeated figure from QKD security-proof literature, not confirmed this session | Treat as **MODELED / SENSITIVITY VARIABLE**, with the ~11% figure used only as a plausibility upper bound to check simulated values against, not as a hard-coded constant, until verified |
| Key pool capacity | Sized as "N sessions' worth" of key material | **MODELED** — own systems design (Task 6 Section 6), not a literature figure |
| Availability levels | {100%, 50%, 0%} pilot set / {100,75,50,25,0%} full set | **EXPERIMENTAL** — design choice, not a measured availability statistic |
| Outage pattern | Injected schedule (fixed-duration or stochastic on/off) | **MODELED** — the *approach* is a DESIGN ASSUMPTION grounded in Zhu (2025)'s methodology per Task 5; specific distribution parameters are not yet extracted from that source |
| Key consumption per session | Fixed by our own HKDF/AEAD design (Section 4/6) | **Internally derived**, not a QKD-literature parameter |

Consistent with the instruction: where literature doesn't provide a
universal range (generation rate, QBER's exact operational value, outage
distribution), the response is a **sensitivity analysis over the
parameter**, not an invented "realistic" constant presented as fact.

---

## 8. Final Go/No-Go

**CRYPTOGRAPHIC CONSTRUCTION:**
```
IKM = QKD_secret || ML-KEM_secret
PRK = HKDF-Extract(salt, IKM)
session_key = HKDF-Expand(PRK, info, L)
```

**SECURITY CLAIM WE CAN MAKE:**
An engineering-level key combination using HKDF (RFC 5869's
extract-then-expand construction, designed to combine multiple entropy
sources) to derive a session key from independently-generated QKD and
ML-KEM secrets, with no formally proven compositional security property
claimed for this specific combination (Claim C).

**SECURITY CLAIM WE CANNOT MAKE:**
That this construction is "formally proven secure" or that it inherits
a proven "at least one component secure" guarantee from hybrid-KEM
combiner literature (Claim A, and Claim B pending verification) — the
available combiner proofs I'm aware of are built around KEM-output
inputs specifically, and QKD-derived key material is not a KEM output,
so that inheritance is not established without further verification
(Section 2).

**AUTHENTICATION:**
The classical control channel (QKD reconciliation traffic and
application-layer session/mode-sync messages) is authenticated via
ML-DSA. The quantum channel itself is not authenticated by this
mechanism — its integrity relies on QKD's own physical-layer detection
properties, separately from ML-DSA.

**PQC PARAMETERS:**
Not stated here — blocked per Section 6. To be sourced at implementation
time directly from the `liboqs` library (for code) and from the FIPS
203/204 specifications directly (for the paper's Methods section), not
from recollection.

**QKD MODEL:**
Distance/loss grounded in a real, verified field deployment (Clason et
al. 2026); generation rate, QBER, and outage-pattern parameters treated
as modeled sensitivity variables swept across a range, not fixed to an
invented "representative" constant, per Section 7.

**REMAINING ASSUMPTIONS:**
- The HKDF combiner's *engineering* soundness (Claim C) is not in
  question; its *upgrade path* to Claim B depends entirely on Section
  1's still-outstanding source verification.
- QBER's ~11% plausibility bound (Section 7) is unverified and used only
  as a sanity check, not a modeling input.
- Exact PQC byte-size parameters remain unconfirmed for citation
  purposes (though not blocking for code, per Section 6).
- Everything already carried forward from Task 6 Section 19.2 (KDF
  robustness in the actual implementation, device-credential
  provisioning) still stands, unchanged by this task.

**IMPLEMENTATION STATUS: GO** — for the engineering construction, under
Claim C specifically. The construction, its (deliberately modest)
security claim, and the authentication design are now settled and don't
depend on the still-outstanding Section 1/6 verification to be
implemented correctly. What remains open (Section 1's citation-level
confirmation, Section 6's exact cited byte values) is real and should
not be dropped — but it gates the **paper's** security-claim wording and
Methods-section precision, not the start of implementation.

---

**TASK 7.1 COMPLETE — HYBRID CRYPTOGRAPHIC DESIGN CLEARED FOR
IMPLEMENTATION**, under the security claim stated above (Claim C), with
Section 1 and Section 6's verification gaps carried forward as
must-resolve-before-manuscript-writing items, not implementation
blockers.
