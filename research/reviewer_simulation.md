# Phase 16: Reviewer Simulation

Three simulated reviews, written from distinct disciplinary vantage points
a real IEEE-journal editor might assign this paper to. Each concern is
checked against what the manuscript actually says (cited by section) before
being marked Addressed, Partially Addressed, or Open. Nothing here is
softened for effect: two concerns are marked Open because the manuscript
itself already concedes them in its own Limitations section, and simulating
a reviewer who did not notice that would be dishonest.

---

## Reviewer 1 (Cryptography / PQC specialist)

**R1.1 --- "Is the hybrid key-combining construction novel, or standard
KEM-combiner practice?"**
The manuscript does not claim the combiner itself is novel; Section
"Alternative Constructions Considered" (`sec:crypto`) explicitly cites the
KEM-combiner security-proof literature and hybrid-TLS deployment precedent
and frames the construction as adopting established practice, not
inventing it. The paper's claimed contribution is the *adaptive
availability-driven switch* between hybrid and PQC-only modes (Algorithm 1),
not the combiner primitive. **Addressed** --- the boundary is stated
explicitly, not left for a reviewer to infer.

**R1.2 --- "All PQC timings are on a general-purpose x86-64 host. Do these
numbers mean anything for the IoMT/embedded endpoints the paper's own
motivation section describes?"**
The manuscript's "This Is a Simulation Study, Not a Hardware Study"
subsection (`sec:limitations`) states this limitation in exactly these
terms, cites the pqm4-family embedded-PQC benchmarking literature as the
appropriate reference point instead, and explicitly declines to claim
embedded-device performance. **Addressed as a disclosed limitation**, not
resolved --- the manuscript is honest that this remains an open empirical
question, which is the correct posture, not a defect to paper over.

**R1.3 --- "The shared-secret mismatch check in the ML-KEM implementation
(fail loud, not fail silent) is good practice, but is it actually exercised
by the test suite, or just present in the code path?"**
Checked directly against `src/crypto/pqc.py` and `tests/test_hybrid_kdf.py`:
the check raises `EstablishmentFailure` on a real mismatch between encap
and decap, but `test_6_ml_kem_failure_is_detected` --- the test whose name
suggests it covers this --- actually exercises a *QKD pool-capacity*
failure (a zero-capacity pool), not an ML-KEM shared-secret mismatch; the
test's own docstring concedes this ("a direct ML-KEM-internal failure is
covered by pqc.py's own shared-secret mismatch guard") without the guard
itself ever being triggered by any test in the 61-test suite. **Open,
confirmed by direct code inspection** --- the correctness safeguard exists
in the implementation but is not independently exercised by the test
suite; a test that corrupts a ciphertext or forces a decap mismatch is a
concrete, low-cost fix worth making before submission.

**RESOLVED (follow-up pass):** `tests/test_pqc.py::test_ml_kem_shared_secret_mismatch_raises`
now monkeypatches `oqs.KeyEncapsulation.decap_secret` to return a
corrupted secret and asserts `establish()` raises `EstablishmentFailure`.
Verified meaningful, not a false-positive: manually neutering the guard
(`if shared_secret_sender != shared_secret_receiver:` -> `if False:`)
was confirmed to make this specific test fail, then the change was
reverted. Full suite: 62/62 passing.

---

## Reviewer 2 (Systems / networking, simulation methodology)

**R2.1 --- "This is a discrete-event simulation with a modeled QKD
rate/pool, not a physical-layer QKD simulation. Why is that an acceptable
scope choice, and is it disclosed prominently enough?"**
The "Implementation Boundary" subsection (`sec:implboundary`) states this
explicitly and in detail, including a paragraph naming the road not taken
(a BB84-style protocol-level simulation) and the specific reason it was
not used. **Addressed** --- disclosed at the level of detail a systems
reviewer would expect, not buried in a single sentence.

**R2.2 --- "A 5-repetitions-per-cell pilot is small for drawing strong
conclusions. Is statistical power addressed?"**
The manuscript's "Pilot Scope, Not Full Study" subsection concedes this
directly, and Table `tab:gonogo`'s go/no-go criteria include using the
pilot's own variance to size a larger follow-up study --- the pilot's stated
purpose includes generating that variance estimate, not standing in as the
final study. **Addressed as a disclosed scope limitation**, consistent with
how the paper frames its own contribution (a pilot-scale characterization,
not a definitive large-sample result).

**R2.3 --- "The bimodal latency finding (median > mean at low QKD
availability) is a real and well-explained statistical observation, but is
it visualized, or only described in prose and a table?"**
Checked: Figure `fig:latency` shows mean with bootstrap CIs on a log scale,
but no histogram or violin/box plot showing the actual bimodal shape is
present in the current figure set. **Open** --- a legitimate ask; the
manuscript's own "Latency Distribution Shape" subsection describes the
effect precisely enough in prose and via the mean/median/p95 table
comparison that the finding is verifiable, but a reviewer could reasonably
request a distributional plot as a revision, and none currently exists.

---

## Reviewer 3 (Healthcare informatics / domain fit)

**R3.1 --- "The dataset is explicitly synthetic, not derived from a
standard synthetic-EHR generator like Synthea. Why, and does this weaken
the healthcare-specific claim?"**
Confirmed against the Phase 1 repository audit (`research/paper_rewrite_audit.md`):
the dataset is not Synthea-derived, and the manuscript does not claim it
is. This is a legitimate scope question --- the paper's payload realism
rests on payload *size class* (medium), not on clinically realistic
synthetic record content, since the object of study is the cryptographic
key-establishment layer, not clinical data modeling. **Partially
Addressed** --- the paper is honest about what the data is, but does not
explicitly justify to a healthcare-informatics reader why payload-size
realism is sufficient for this paper's specific research question rather
than full EHR-content realism; a sentence doing so explicitly would
strengthen this for that specific reviewer audience. **Open** as a
suggested (not required) clarification.

**R3.2 --- "Emergency-access transactions are mentioned in the motivating
scenario, but does the pilot actually model differentiated latency
tolerance by transaction class?"**
Checked against Table `tab:hypothesissummary` and the H2 discussion in
`sec:discussion`: the manuscript's own hypothesis-summary table marks this
test as incomplete in the current pilot design, and the Discussion section
states this directly rather than implying the emergency/routine distinction
was fully evaluated. **Addressed as an honestly disclosed gap** --- the
paper does not overclaim here, which is the right call, but it does mean
the motivating scenario's emergency-access framing is aspirational for
future work rather than something this pilot's results directly test.

**R3.3 --- "6G-edge topology claims: is there anything 6G-specific being
tested, or is this a generic edge-network latency model with a 6G label
attached?"**
Checked against `sec:sixg` and the "Relationship to URLLC-Class Latency
Targets" subsection: the manuscript explicitly concedes the 6G layer is
"three generic hops with configurable, not standards-derived, parameters,"
and separately declines to adopt a URLLC-class figure as its own pass/fail
threshold, stating clearly why. **Addressed as an honestly scoped claim**
--- the paper does not claim standards-grounded 6G-specific behavior, and
says so plainly rather than trading on the "6G" framing for unearned
specificity.

---

## Summary

| # | Concern | Status |
|---|---|---|
| R1.1 | Combiner novelty vs. adaptivity novelty | Addressed |
| R1.2 | General-purpose host, not embedded hardware | Addressed (disclosed limitation) |
| R1.3 | Shared-secret-mismatch path test coverage | **Open** |
| R2.1 | QKD is a rate/pool model, not physical-layer sim | Addressed |
| R2.2 | Small pilot repetition count | Addressed (disclosed scope) |
| R2.3 | No distributional plot for the bimodal finding | **Open** |
| R3.1 | Synthetic, non-Synthea dataset justification | Open (suggested clarification) |
| R3.2 | Emergency-vs-routine latency differentiation untested | Addressed (disclosed gap) |
| R3.3 | 6G-specificity of the network model | Addressed (disclosed scope) |

Two items (R1.3, R2.3) are genuine open items worth acting on before
submission; R3.1 is a suggested, non-blocking clarification. Everything
else the manuscript already discloses honestly in its own text --- the
simulated reviewers did not find anything the paper is hiding, which is
itself a check on the paper's own self-critical sections, not a claim that
no further review would surface anything else.
