"""
QKD modeled as a SIMULATED RESOURCE (Task 8 Phase 6). This module does
NOT simulate photons, basis reconciliation, or any quantum-mechanical
process -- per the explicit instruction, and consistent with Task 6
Section 17's "will model abstractly, not implement" boundary.

The model: a bounded key-material pool that fills at a configurable
generation rate and drains as sessions consume material from it. On
insufficient/unavailable material, `draw()` raises -- it does NOT fall
back to anything. Fallback is the adaptive controller's job (Task 8
Phase 6's explicit instruction), not this module's.

Parameter provenance (Task 7 Part 3 / Task 7.1 Section 7):
  - Distance/loss figures used only as loose plausibility context
    (Clason et al. 2026, LITERATURE-MEASURED) -- not used to derive a
    hard-coded rate here.
  - generation_rate_bits_per_sec, capacity_bits, and QBER are all
    MODELED / SENSITIVITY VARIABLES, explicitly configurable and swept,
    never hard-coded as a single "the" QKD rate.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class QKDInsufficientMaterial(Exception):
    """Raised by draw() when the pool cannot satisfy a request.

    This is a normal, expected condition (not a bug) -- callers
    (baselines, the adaptive controller) are expected to catch this and
    decide what to do. This module does not decide that for them.
    """


@dataclass
class QKDPoolConfig:
    """All values here are MODELED ASSUMPTIONS / SENSITIVITY VARIABLES
    per Task 7 Part 3 and Task 7.1 Section 7 -- not literature-measured
    facts. See implementation/config/pilot.yaml for the values actually
    used in a given experiment run, and
    docs/implementation_notes.md for the parameter-provenance table.
    """

    capacity_bits: int
    generation_rate_bits_per_sec: float
    qber: float = 0.0  # quantum bit error rate; 0.0 = ideal channel, no loss modeled yet
    initial_fill_fraction: float = 1.0  # pool starts full by default


@dataclass
class QKDPool:
    """A bounded buffer of QKD-generated key material.

    `level_bits` is the current fill level. `available_fraction()` is
    what the adaptive controller (Task 6 Section 4) reads to make its
    HYBRID vs. PQC_ONLY decision -- this class does not make that
    decision itself.
    """

    config: QKDPoolConfig
    level_bits: float = field(init=False)
    _outage: bool = field(default=False, init=False)

    def __post_init__(self):
        self.level_bits = self.config.capacity_bits * self.config.initial_fill_fraction

    def tick(self, elapsed_seconds: float) -> None:
        """Advance simulated time, generating new key material unless
        an outage is currently active (set_outage(True))."""
        if self._outage:
            return
        generated = self.config.generation_rate_bits_per_sec * elapsed_seconds
        self.level_bits = min(self.config.capacity_bits, self.level_bits + generated)

    def set_outage(self, active: bool) -> None:
        """Inject or clear a QKD channel outage (Task 6 Section 7,
        Threat E / Task 7 Part 3 "outage duration/pattern"). While
        active, tick() does not replenish the pool -- draws still
        deplete it normally, matching Task 6 Section 6's "QKD link
        fails -> pool drains toward 0" behavior."""
        self._outage = active

    @property
    def in_outage(self) -> bool:
        return self._outage

    def available_fraction(self) -> float:
        if self.config.capacity_bits == 0:
            return 0.0
        return self.level_bits / self.config.capacity_bits

    def draw(self, n_bits: int) -> bytes:
        """Consume n_bits of key material from the pool and return it
        as bytes. Raises QKDInsufficientMaterial if unavailable -- does
        NOT fall back to anything (Task 8 Phase 6)."""
        if self.level_bits < n_bits:
            raise QKDInsufficientMaterial(
                f"requested {n_bits} bits, pool has {self.level_bits:.0f} bits "
                f"({self.available_fraction():.1%} of capacity)"
            )
        self.level_bits -= n_bits
        # The pool models *availability*, not the actual bit values a
        # real QKD system would produce (those come from photon
        # detection events, explicitly out of scope -- Task 8 Phase 6).
        # We generate cryptographically random bytes to stand in for
        # "genuinely unpredictable key material of the requested
        # length" -- this is a modeling stand-in, not a claim that this
        # randomness source has QKD's information-theoretic security
        # property. Documented explicitly in
        # docs/implementation_notes.md.
        import os

        n_bytes = (n_bits + 7) // 8
        return os.urandom(n_bytes)
