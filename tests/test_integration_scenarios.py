"""
Integration tests -- Task 8 Phase 16's exact five required scenarios:

  1. QKD available -> hybrid
  2. QKD unavailable -> PQC fallback
  3. QKD-only + outage -> failure
  4. static hybrid + outage -> expected failure behavior
  5. adaptive hybrid + outage -> PQC fallback

Each test exercises the real baseline objects end-to-end (real PQC
operations via liboqs, real QKD pool draws) -- these are not mocked.
"""

from src.adaptive.controller import AdaptiveController, AdaptiveThresholds, Criticality
from src.baselines.baselines import BaselineID, build_baseline
from src.crypto.interfaces import KeySource
from src.crypto.qkd import QKDPool, QKDPoolConfig

THRESHOLDS = AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.001)


def _full_pool():
    return QKDPool(QKDPoolConfig(capacity_bits=100_000, generation_rate_bits_per_sec=1000))


def _empty_pool():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0))
    pool.set_outage(True)
    try:
        pool.draw(999)
    except Exception:
        pass
    return pool


def test_1_qkd_available_selects_hybrid():
    controller = AdaptiveController(THRESHOLDS)
    baseline = build_baseline(BaselineID.B5_ADAPTIVE, controller)
    context = {"qkd_pool": _full_pool(), "context_label": b"it1", "criticality": Criticality.ROUTINE}
    result = baseline.establish_session_key(context)
    assert result.success is True
    assert result.key.source == KeySource.ADAPTIVE_HYBRID
    assert result.controller_state == "qkd_available"
    baseline.close()


def test_2_qkd_unavailable_triggers_pqc_fallback():
    controller = AdaptiveController(THRESHOLDS)
    baseline = build_baseline(BaselineID.B5_ADAPTIVE, controller)
    context = {"qkd_pool": _empty_pool(), "context_label": b"it2", "criticality": Criticality.ROUTINE}
    result = baseline.establish_session_key(context)
    assert result.success is True  # fallback succeeds, just in a different mode
    assert result.key.source == KeySource.PQC_ONLY
    assert result.controller_state == "qkd_unavailable"
    baseline.close()


def test_3_qkd_only_plus_outage_fails():
    baseline = build_baseline(BaselineID.B3_QKD_ONLY)
    context = {"qkd_pool": _empty_pool(), "context_label": b"it3"}
    result = baseline.establish_session_key(context)
    assert result.success is False
    assert result.key is None
    assert result.failure_reason is not None
    baseline.close()


def test_4_static_hybrid_plus_outage_fails_not_falls_back():
    """Task 8 Phase 12's explicit warning: B4 does NOT automatically
    behave like B5. Under outage, it must fail, not silently switch to
    PQC-only."""
    baseline = build_baseline(BaselineID.B4_STATIC_HYBRID)
    context = {"qkd_pool": _empty_pool(), "context_label": b"it4"}
    result = baseline.establish_session_key(context)
    assert result.success is False
    assert result.key is None
    baseline.close()


def test_5_adaptive_hybrid_plus_outage_falls_back_to_pqc():
    controller = AdaptiveController(THRESHOLDS)
    baseline = build_baseline(BaselineID.B5_ADAPTIVE, controller)
    context = {"qkd_pool": _empty_pool(), "context_label": b"it5", "criticality": Criticality.ROUTINE}
    result = baseline.establish_session_key(context)
    assert result.success is True
    assert result.key.source == KeySource.PQC_ONLY
    baseline.close()


def test_b4_vs_b5_diverge_under_outage_the_critical_distinction():
    """The single most important behavioral distinction in this whole
    project (Task 8 Phase 12): B4 fails under outage, B5 gracefully
    falls back. Both are tested together here to make the contrast
    explicit in one place, not just implied by two separate tests."""
    pool_b4 = _empty_pool()
    pool_b5 = _empty_pool()

    b4 = build_baseline(BaselineID.B4_STATIC_HYBRID)
    controller = AdaptiveController(THRESHOLDS)
    b5 = build_baseline(BaselineID.B5_ADAPTIVE, controller)

    r4 = b4.establish_session_key({"qkd_pool": pool_b4, "context_label": b"contrast"})
    r5 = b5.establish_session_key(
        {"qkd_pool": pool_b5, "context_label": b"contrast", "criticality": Criticality.ROUTINE}
    )

    assert r4.success is False, "B4 must fail under outage (no fallback)"
    assert r5.success is True, "B5 must succeed under outage (via fallback)"
    assert r5.key.source == KeySource.PQC_ONLY

    b4.close()
    b5.close()
