"""Unit tests for the adaptive controller (Task 8 Phase 16)."""

from src.adaptive.controller import (
    AdaptiveController,
    AdaptiveThresholds,
    ControllerState,
    Criticality,
    Mode,
)
from src.crypto.qkd import QKDPool, QKDPoolConfig

THRESHOLDS = AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.0)


def test_high_availability_selects_hybrid():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0, initial_fill_fraction=1.0))
    controller = AdaptiveController(THRESHOLDS)
    decision = controller.select_mode(pool, Criticality.ROUTINE)
    assert decision.mode == Mode.HYBRID
    assert decision.state == ControllerState.QKD_AVAILABLE


def test_exhausted_pool_selects_pqc_only():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0, initial_fill_fraction=0.0))
    controller = AdaptiveController(THRESHOLDS)
    decision = controller.select_mode(pool, Criticality.ROUTINE)
    assert decision.mode == Mode.PQC_ONLY
    assert decision.state == ControllerState.QKD_UNAVAILABLE


def test_emergency_never_waits_even_when_degraded():
    """Task 6 Section 4: emergency-flagged transactions never wait,
    regardless of pool state."""
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0, initial_fill_fraction=0.2))
    controller = AdaptiveController(THRESHOLDS)
    decision = controller.select_mode(pool, Criticality.EMERGENCY)
    assert decision.waited is False
    assert decision.mode == Mode.PQC_ONLY


def test_degraded_routine_transaction_waits():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0, initial_fill_fraction=0.2))
    controller = AdaptiveController(THRESHOLDS)
    waited_flag = []

    def fake_wait(seconds):
        waited_flag.append(seconds)

    decision = controller.select_mode(pool, Criticality.ROUTINE, wait_fn=fake_wait)
    assert decision.waited is True
    assert len(waited_flag) == 1


def test_wait_that_recovers_above_threshold_selects_hybrid():
    """A pool that replenishes above pool_min_hybrid during the wait
    should result in HYBRID -- confirms wait_fn's side effects (via
    pool.tick(), called by the caller during the wait) are correctly
    observed after the wait."""
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=1000, initial_fill_fraction=0.2))
    controller = AdaptiveController(THRESHOLDS)

    def wait_and_replenish(seconds):
        pool.tick(seconds)

    decision = controller.select_mode(pool, Criticality.ROUTINE, wait_fn=wait_and_replenish)
    # generation_rate=1000 bits/sec * wait_timeout_seconds=0.0 -> no
    # actual replenishment at this threshold config; use a nonzero
    # timeout variant to exercise the recovery path explicitly:
    thresholds_with_wait = AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=1.0)
    controller2 = AdaptiveController(thresholds_with_wait)
    decision2 = controller2.select_mode(pool, Criticality.ROUTINE, wait_fn=wait_and_replenish)
    assert decision2.mode == Mode.HYBRID
    assert decision2.waited is True


def test_does_not_alter_cryptographic_primitives():
    """Task 8 Phase 11: 'The controller must NOT alter cryptographic
    primitives. It only chooses the available key-establishment mode.'
    Confirms the controller's public surface returns only a mode/state
    decision -- it has no method that touches key material."""
    controller = AdaptiveController(THRESHOLDS)
    public_methods = [m for m in dir(controller) if not m.startswith("_")]
    assert public_methods == ["select_mode"]
