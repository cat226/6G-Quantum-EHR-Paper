# Scope and Claims Boundary

**Project:** Latency-Aware Adaptive QKD-PQC Key Establishment for Electronic
Health Record Sharing in 6G-Edge Healthcare Networks
**Authors:** Ramana Sree K V, Verona Ann Mariya

This document fixes what this project does and does not claim. It exists so
that the boundary is decided deliberately, in advance of running the pilot,
rather than being negotiated after results exist — and so that a reviewer
cannot read a claim into the results that the method does not support.

**This is a simulation study. It is not a hardware study.**

---

## 1. What this project is

A discrete-event simulation comparing five key-establishment strategies
(B1–B5) for EHR sharing across a simplified 6G-edge network abstraction,
under varying QKD availability.

Its contribution is the **comparative behaviour of the five strategies
under QKD degradation and outage** — in particular the distinction between a
static hybrid (B4), which fails when QKD is unavailable, and an adaptive
hybrid (B5), which falls back to a PQC-only path and continues to operate.

Cryptographic operations are **real**, not mocked: ML-KEM-768 and ML-DSA-65
execute through `liboqs`, AES-256-GCM and HKDF through `cryptography`. What
is simulated is the *network, workload, and QKD resource*, not the
cryptography.

## 2. What this project is not

It is **not** a hardware study, a device-feasibility study, an embedded
benchmarking effort, or an implementation-performance study of PQC on
constrained platforms.

Accordingly, this project makes **no claim** about:

- the performance of ML-KEM-768 or ML-DSA-65 on constrained microcontrollers
  (ARM Cortex-M4 or any other embedded target);
- whether a given class of IoMT device can or cannot perform ML-DSA-65
  signature generation within a real-time deadline;
- cycle counts, energy consumption, memory footprint, or code size on any
  embedded platform;
- the necessity or benefit of offloading signature generation from endpoint
  devices to an Edge Gateway.

These are legitimate research questions. They are not this project's
questions, and this project's method cannot answer them.

## 3. Why the boundary sits here

The simulation measures cryptographic cost by executing the real primitives
on the **host machine running the simulation** — an x86-64 server
(see `docs/environment_manifest.md`). Measured single-operation timings in
the validated environment are on the order of:

```
ML-KEM-768   keygen ~1.7 ms   encap ~0.1 ms   decap ~0.02 ms
ML-DSA-65    keygen ~0.1 ms   sign  ~0.1 ms   verify ~0.04 ms
```

There is no device-class model in the simulation: no per-device processing
profile, no clock-rate parameter, no cycle-count mapping. Every endpoint in
the topology is, computationally, the host CPU.

That is a legitimate simplification for a study about **adaptive strategy
selection under QKD availability** — the comparison between B1–B5 is
internally fair because every baseline is measured on the same hardware
under the same conditions. It is *not* a legitimate basis for statements
about embedded feasibility, because a constrained endpoint would produce
timings differing by orders of magnitude, and the simulation contains no
model of that difference.

Stating this plainly costs the project nothing. The B4-versus-B5 result —
that a static hybrid creates a single point of failure while an adaptive
hybrid degrades gracefully — does not depend on endpoint hardware at all.

## 4. Rules for reporting

When writing the manuscript:

**Report cryptographic timings as what they are.** Use wording of the form
"measured on the simulation host (x86-64; see environment manifest)". Do not
attribute a measured latency to "an IoMT device", "a wearable", "a
constrained endpoint", or "the edge gateway" as though the number
characterises that hardware. The topology positions are simulation roles,
not distinct hardware profiles.

**Do not present the offload architecture as an empirical finding.** The
architecture places signature operations at the Edge Gateway and Hospital
Core. That is a design decision inherited from Task 6, and it may well be
sound — but this simulation does not test it and must not be cited as
evidence for it. If the manuscript discusses offload, it belongs in
design rationale or related work, with the supporting claim cited to
external literature, not to these results.

**Latency budgets are context, not measurement.** A 6G URLLC reference
figure (commonly cited as sub-millisecond) may be used to give measured
key-establishment latency context — for example, plotting a reference line.
It must not be presented as a budget this simulation verifies compliance
with, because the simulation does not model the rest of the protocol stack
that would consume that budget.

**Network parameters are modelled assumptions.** Propagation delay,
processing delay, transmission rate, packet loss, and edge processing
delay are configurable simulation parameters chosen to be plausible, not
measurements of any deployed 6G system. 6G standards are not finalised, and
this simulation does not implement a 6G protocol stack — no PHY, no MAC,
no radio protocol.

**QKD parameters are modelled assumptions.** Pool capacity, generation rate,
and the availability-to-rate mapping are sensitivity variables, not
literature-measured facts. No experimental QKD hardware result is claimed,
and no quantum-physical process is simulated — no photons, no basis
reconciliation. See `docs/implementation_notes.md` Part II §5 for the full
parameter-provenance table.

**The hybrid construction claim is unchanged.** The HKDF combination of a
QKD secret with an ML-KEM shared secret is an **engineering-level key
combination**. No compositional security proof is claimed for this
instantiation. The exact wording is pinned in code as
`src.crypto.hybrid.SECURITY_CLAIM` and must not be strengthened.

## 5. What remains in scope and unimplemented

Recorded so these are not mistaken for claims the project already supports.
They are simulation-level items — none requires hardware work:

| Item | Status |
|---|---|
| Per-hop network differentiation | Access, edge, and backbone links currently share one identical parameter set |
| Throughput and CPU/memory metrics | Not collected |
| Communication-overhead decomposition | Recorded as a single scalar; signature share vs KEM share not separable from raw data |
| Control-plane / user-plane separation | Not modelled; a design direction only |
| ETSI GS QKD 014 / 020 conformance mapping | Not documented |
| Between-baseline hypothesis testing | Not implemented |

Each is a bounded simulation change if the project later wants it. None
changes the scope boundary in Sections 2–4.

---

**Summary in one line:** this project studies *strategy selection under QKD
availability*, measured in simulation with real cryptography on a
general-purpose host — and claims nothing about embedded hardware.
