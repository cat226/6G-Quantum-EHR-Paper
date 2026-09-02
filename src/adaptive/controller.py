"""
The adaptive controller (Task 6 Section 4, Task 8 Phase 11).

Decides HYBRID vs. PQC_ONLY based on QKD pool state and configured
thresholds. Per the explicit instruction: the controller does NOT alter
cryptographic primitives -- it only chooses which key-establishment mode
a baseline uses. It does not itself perform key establishment.

Explicit states (Task 8 Phase 11):
  QKD_AVAILABLE   -- pool comfortably above the hybrid threshold
  QKD_DEGRADED    -- below the hybrid threshold but above the wait
                     threshold; a bounded wait may be attempted
  QKD_UNAVAILABLE -- below the wait threshold; no wait, immediate
                     PQC_ONLY
  PQC_FALLBACK    -- the resulting *decision* state when PQC_ONLY is
                     chosen (as distinct from QKD_UNAVAILABLE, which is
                     a *pool* state -- PQC_FALLBACK can also result from
                     a QKD_DEGRADED wait that timed out without the pool
                     recovering above threshold)

Per Task 6 modification #1 (approved in Task 6's review) and Task 7's
modification acknowledgment: clinical criticality is treated only as an
input that can *skip the wait* for degraded conditions (an
emergency-flagged transaction never waits) -- it is not a primary
decision axis and is not swept as an independent variable in the pilot.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..crypto.qkd import QKDPool


class Criticality(str, Enum):
    ROUTINE = "routine"
    EMERGENCY = "emergency"


class Mode(str, Enum):
    HYBRID = "hybrid"
    PQC_ONLY = "pqc_only"


class ControllerState(str, Enum):
    QKD_AVAILABLE = "qkd_available"
    QKD_DEGRADED = "qkd_degraded"
    QKD_UNAVAILABLE = "qkd_unavailable"
    PQC_FALLBACK = "pqc_fallback"


@dataclass
class AdaptiveThresholds:
    """Threshold configuration (Task 6 Section 4's `thresholds` object).

    All MODELED ASSUMPTIONS -- see docs/implementation_notes.md and
    implementation/config/pilot.yaml for the values used in a given run.
    """

    pool_min_hybrid: float  # fraction [0,1]; >= this -> HYBRID immediately
    pool_min_wait: float  # fraction [0,1]; below this -> no wait, PQC_ONLY
    wait_timeout_seconds: float  # bounded wait for non-emergency transactions


@dataclass
class ControllerDecision:
    mode: Mode
    state: ControllerState
    waited: bool
    wait_seconds: float
    pool_fraction_at_decision: float


class AdaptiveController:
    """Implements Task 6 Section 4's select_mode() pseudocode as real
    code against a live QKDPool."""

    def __init__(self, thresholds: AdaptiveThresholds):
        self._thresholds = thresholds

    def select_mode(
        self,
        pool: QKDPool,
        criticality: Criticality = Criticality.ROUTINE,
        wait_fn=None,
    ) -> ControllerDecision:
        """`wait_fn(seconds)` is injected so the simulation harness can
        advance simulated time (SimPy) rather than this controller
        calling a real-time sleep -- keeping the controller decoupled
        from the simulation engine, per Task 8 Phase 3's interface
        discipline."""
        fraction = pool.available_fraction()

        if fraction >= self._thresholds.pool_min_hybrid:
            return ControllerDecision(
                mode=Mode.HYBRID,
                state=ControllerState.QKD_AVAILABLE,
                waited=False,
                wait_seconds=0.0,
                pool_fraction_at_decision=fraction,
            )

        if criticality == Criticality.EMERGENCY:
            # Emergency transactions never wait, regardless of pool state
            # (Task 6 Section 4's explicit design decision).
            return ControllerDecision(
                mode=Mode.PQC_ONLY,
                state=ControllerState.PQC_FALLBACK,
                waited=False,
                wait_seconds=0.0,
                pool_fraction_at_decision=fraction,
            )

        if fraction >= self._thresholds.pool_min_wait:
            # Degraded but not exhausted: bounded wait for replenishment.
            if wait_fn is not None:
                wait_fn(self._thresholds.wait_timeout_seconds)
            fraction_after = pool.available_fraction()
            if fraction_after >= self._thresholds.pool_min_hybrid:
                return ControllerDecision(
                    mode=Mode.HYBRID,
                    state=ControllerState.QKD_AVAILABLE,
                    waited=True,
                    wait_seconds=self._thresholds.wait_timeout_seconds,
                    pool_fraction_at_decision=fraction_after,
                )
            return ControllerDecision(
                mode=Mode.PQC_ONLY,
                state=ControllerState.PQC_FALLBACK,
                waited=True,
                wait_seconds=self._thresholds.wait_timeout_seconds,
                pool_fraction_at_decision=fraction_after,
            )

        # Pool effectively exhausted.
        return ControllerDecision(
            mode=Mode.PQC_ONLY,
            state=ControllerState.QKD_UNAVAILABLE,
            waited=False,
            wait_seconds=0.0,
            pool_fraction_at_decision=fraction,
        )
