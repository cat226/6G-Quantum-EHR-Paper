"""
Regression tests for the B5 adaptive bounded-wait path (Task 8.5).

Background: `B5Adaptive.establish_session_key()` originally called
`select_mode(pool, criticality)` without a `wait_fn`. The controller only
performs its bounded wait when one is injected, so the degraded-band wait
never happened during a simulation run: no simulated time passed, the pool
never replenished, and the decision was always an immediate PQC fallback --
while still being *recorded* as `waited=True`. `wait_timeout_seconds` was
therefore inert in `config/pilot.yaml`.

These tests pin the observable behaviour of the wait path so it cannot
silently regress. They deliberately assert on *outcomes* -- selected mode,
QKD availability, simulated elapsed time, fallback, success/failure -- and
never on how the wait is plumbed internally.

Thresholds below use the pilot's values (pool_min_hybrid=0.3,
pool_min_wait=0.1) so a pool at 20% capacity sits squarely in the degraded
band, which is the band the wait path exists to serve.
"""

import time

import pytest

from src.adaptive.controller import (
    AdaptiveController,
    AdaptiveThresholds,
    ControllerState,
    Criticality,
    Mode,
)
from src.baselines.baselines import QKD_BITS_PER_SESSION, BaselineID, build_baseline
from src.crypto.interfaces import KeySource
from src.crypto.qkd import QKDPool, QKDPoolConfig

#: Capacity comfortably above one session's draw, so a HYBRID decision can
#: actually be serviced once the pool recovers.
CAPACITY_BITS = 4 * QKD_BITS_PER_SESSION  # 1024 bits

#: 20% of capacity: below pool_min_hybrid (0.3), above pool_min_wait (0.1).
DEGRADED_FILL = 0.2


def _thresholds(wait_timeout_seconds: float) -> AdaptiveThresholds:
    return AdaptiveThresholds(
        pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=wait_timeout_seconds
    )


def _degraded_pool(generation_rate_bits_per_sec: float, outage: bool = False) -> QKDPool:
    """A pool sitting in the degraded band, with a configurable refill rate."""
    pool = QKDPool(
        QKDPoolConfig(
            capacity_bits=CAPACITY_BITS,
            generation_rate_bits_per_sec=generation_rate_bits_per_sec,
            initial_fill_fraction=DEGRADED_FILL,
        )
    )
    if outage:
        pool.set_outage(True)
    return pool


def _b5(wait_timeout_seconds: float):
    return build_baseline(
        BaselineID.B5_ADAPTIVE, AdaptiveController(_thresholds(wait_timeout_seconds))
    )


def _routine_context(pool: QKDPool, label: bytes) -> dict:
    return {"qkd_pool": pool, "context_label": label, "criticality": Criticality.ROUTINE}


# --------------------------------------------------------------------------
# TEST A -- degraded, and QKD becomes available during the bounded wait
# --------------------------------------------------------------------------


def test_a_degraded_pool_that_recovers_during_wait_selects_hybrid():
    """The whole point of the wait: a pool that refills past
    pool_min_hybrid while B5 waits must produce a HYBRID session, not a
    fallback.

    Refill rate is set so one wait interval carries the pool from 20%
    (degraded) to full -- comfortably across the 30% hybrid threshold.
    """
    pool = _degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS)
    assert pool.available_fraction() == pytest.approx(DEGRADED_FILL)

    baseline = _b5(wait_timeout_seconds=1.0)
    result = baseline.establish_session_key(_routine_context(pool, b"wait-A"))

    assert result.success is True
    assert result.key.source == KeySource.ADAPTIVE_HYBRID, (
        "a pool that recovered during the bounded wait must yield a hybrid key"
    )
    assert result.controller_state == ControllerState.QKD_AVAILABLE.value
    assert result.wait_seconds == pytest.approx(1.0)
    baseline.close()


# --------------------------------------------------------------------------
# TEST B -- degraded, and QKD does NOT become available
# --------------------------------------------------------------------------


def test_b_degraded_pool_that_does_not_recover_falls_back_to_pqc():
    """Waiting through an outage must not invent key material. The pool is
    in the degraded band but under outage, so no amount of waiting refills
    it -- B5 must fall back and still succeed."""
    pool = _degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS, outage=True)
    level_before = pool.level_bits

    baseline = _b5(wait_timeout_seconds=1.0)
    result = baseline.establish_session_key(_routine_context(pool, b"wait-B"))

    assert result.success is True, "fallback must succeed, not fail"
    assert result.key.source == KeySource.PQC_ONLY
    assert result.controller_state == ControllerState.PQC_FALLBACK.value
    assert pool.level_bits == level_before, "an outage must not replenish during the wait"
    baseline.close()


# --------------------------------------------------------------------------
# TEST C -- degraded, wait disabled
# --------------------------------------------------------------------------


def test_c_zero_wait_timeout_falls_back_immediately():
    """With wait_timeout_seconds=0 the pool gets no chance to recover, even
    at a refill rate that would otherwise rescue it within a full interval.
    This is the behaviour the pre-fix code exhibited *unconditionally*; it
    must now happen only when the wait is actually configured to zero."""
    pool = _degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS)
    level_before = pool.level_bits

    baseline = _b5(wait_timeout_seconds=0.0)
    result = baseline.establish_session_key(_routine_context(pool, b"wait-C"))

    assert result.success is True
    assert result.key.source == KeySource.PQC_ONLY
    assert result.wait_seconds == pytest.approx(0.0)
    assert pool.level_bits == level_before, "a zero-length wait must not advance the pool"
    baseline.close()


def test_c2_wait_timeout_changes_the_outcome_all_else_equal():
    """The sharpest statement of the bug: identical pools, identical
    criticality, differing ONLY in wait_timeout_seconds, must reach
    different modes. Before the fix both returned PQC_ONLY."""
    waited = _b5(wait_timeout_seconds=1.0)
    not_waited = _b5(wait_timeout_seconds=0.0)

    r_wait = waited.establish_session_key(
        _routine_context(_degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS), b"c2-wait")
    )
    r_nowait = not_waited.establish_session_key(
        _routine_context(_degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS), b"c2-nowait")
    )

    assert r_wait.key.source == KeySource.ADAPTIVE_HYBRID
    assert r_nowait.key.source == KeySource.PQC_ONLY
    waited.close()
    not_waited.close()


# --------------------------------------------------------------------------
# TEST D -- B4 must stay static under the same conditions
# --------------------------------------------------------------------------


def test_d_b4_does_not_gain_a_wait_or_a_fallback():
    """B4 is static by definition. Under the same degraded pool that B5
    now waits through, B4 must neither wait nor fall back -- it fails."""
    pool = _degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS)
    assert pool.level_bits < QKD_BITS_PER_SESSION, "pool must be too low to serve a hybrid draw"

    baseline = build_baseline(BaselineID.B4_STATIC_HYBRID)
    result = baseline.establish_session_key(
        {"qkd_pool": pool, "context_label": b"wait-D"}
    )

    assert result.success is False, "B4 must fail rather than fall back"
    assert result.key is None
    assert result.failure_reason is not None
    assert result.wait_seconds == 0.0, "B4 must never wait"
    baseline.close()


def test_d2_b4_and_b5_still_diverge_under_the_degraded_condition():
    """The critical project-level distinction, re-asserted specifically for
    the wait path: same degraded pool, B4 fails, B5 recovers via the wait."""
    b4 = build_baseline(BaselineID.B4_STATIC_HYBRID)
    b5 = _b5(wait_timeout_seconds=1.0)

    r4 = b4.establish_session_key(
        {"qkd_pool": _degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS),
         "context_label": b"d2"}
    )
    r5 = b5.establish_session_key(
        _routine_context(_degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS), b"d2")
    )

    assert r4.success is False, "B4 must fail under the degraded pool"
    assert r5.success is True, "B5 must succeed under the same degraded pool"
    assert r5.key.source == KeySource.ADAPTIVE_HYBRID
    b4.close()
    b5.close()


# --------------------------------------------------------------------------
# TEST E -- the wait advances SIMULATED time, never wall-clock time
# --------------------------------------------------------------------------


def test_e_wait_advances_simulated_time_not_wall_clock():
    """A 30-second bounded wait must cost ~30 simulated seconds of pool
    replenishment and ~0 seconds of real time. A `time.sleep()`-based
    implementation would fail this test by taking 30 real seconds.

    The refill rate is deliberately too low to cross the hybrid threshold,
    so this test observes the *clock*, not the mode decision.
    """
    simulated_wait = 30.0
    rate = 1.0  # bits/sec -- 30 bits over the whole wait; nowhere near threshold
    pool = _degraded_pool(generation_rate_bits_per_sec=rate)
    level_before = pool.level_bits

    baseline = _b5(wait_timeout_seconds=simulated_wait)
    real_start = time.perf_counter()
    result = baseline.establish_session_key(_routine_context(pool, b"wait-E"))
    real_elapsed = time.perf_counter() - real_start

    # Simulated time genuinely advanced: the pool refilled by rate * wait.
    assert pool.level_bits == pytest.approx(level_before + rate * simulated_wait)
    assert result.wait_seconds == pytest.approx(simulated_wait)

    # Real time did not. Generous bound -- real cost here is ML-KEM/ML-DSA
    # operations measured in milliseconds.
    assert real_elapsed < 5.0, (
        f"bounded wait consumed {real_elapsed:.1f}s of wall-clock time; "
        "the wait must be simulated, never a real sleep"
    )
    assert real_elapsed < simulated_wait / 2

    # Still a fallback -- the pool never crossed the hybrid threshold.
    assert result.key.source == KeySource.PQC_ONLY
    baseline.close()


def test_e2_emergency_transactions_still_skip_the_wait():
    """The wait must not have been wired in a way that overrides the
    existing emergency policy: emergency transactions never wait."""
    pool = _degraded_pool(generation_rate_bits_per_sec=CAPACITY_BITS)
    level_before = pool.level_bits

    baseline = _b5(wait_timeout_seconds=1.0)
    result = baseline.establish_session_key(
        {"qkd_pool": pool, "context_label": b"wait-E2", "criticality": Criticality.EMERGENCY}
    )

    assert result.wait_seconds == 0.0
    assert result.key.source == KeySource.PQC_ONLY
    assert pool.level_bits == level_before, "an emergency transaction must not advance the pool"
    baseline.close()


# --------------------------------------------------------------------------
# TEST F -- determinism
# --------------------------------------------------------------------------


def test_f_wait_path_is_deterministic_across_identical_runs():
    """Identical pool configuration and identical transaction sequence must
    produce an identical sequence of decisions. Key material is randomised
    by design; the decision path must not be."""

    def run_sequence():
        pool = _degraded_pool(generation_rate_bits_per_sec=200.0)
        baseline = _b5(wait_timeout_seconds=0.5)
        observed = []
        for i in range(6):
            r = baseline.establish_session_key(_routine_context(pool, f"f-{i}".encode()))
            observed.append(
                (r.success, r.key.source if r.key else None, r.controller_state,
                 round(r.wait_seconds, 9), round(pool.level_bits, 6))
            )
        baseline.close()
        return observed

    first, second = run_sequence(), run_sequence()
    assert first == second, "the wait path must be deterministic under identical inputs"

    # The sequence must actually exercise the wait, or this proves nothing.
    assert any(w > 0 for (_, _, _, w, _) in first), "no wait occurred; test is vacuous"


# --------------------------------------------------------------------------
# Simulator integration -- SimPy clock stays in lockstep with the pool
# --------------------------------------------------------------------------


def test_simulator_advances_simpy_clock_by_the_wait_interval(tmp_path):
    """End-to-end check that the harness charges the bounded wait to the
    simulation clock. Two otherwise identical single-device cells differing
    only in wait_timeout_seconds must not land their transactions at the
    same simulated timestamps.

    Sizing note: at qkd_availability=0.0 the pool starts full
    (20 sessions' worth) and only drains, so the degraded band is not
    reached until roughly the 16th transaction. The cell below therefore
    runs 20 transactions on a single device -- still a unit-scale run, not
    a pilot cell. The fallback assertion below guards against this test
    silently becoming vacuous if that arithmetic ever changes.
    """
    simpy = pytest.importorskip("simpy")  # noqa: F841
    import json

    from src.simulation.simulator import CellConfig, run_cell
    from src.workload.ehr_generator import PayloadClass

    def events_for(wait_timeout_seconds: float):
        cfg = CellConfig(
            experiment_id=f"wait-lockstep-{wait_timeout_seconds}",
            baseline_id=BaselineID.B5_ADAPTIVE,
            qkd_availability_config=0.0,  # pool only drains -> degraded band reached
            device_count=1,
            payload_class=PayloadClass.SMALL,
            network_load="nominal",
            seed=7,
            n_transactions_per_device=20,
            sim_duration_seconds=500.0,
        )
        path = run_cell(
            cfg,
            str(tmp_path / str(wait_timeout_seconds)),
            lambda: AdaptiveController(_thresholds(wait_timeout_seconds)),
        )
        with open(path) as fh:
            return [json.loads(line) for line in fh if line.strip()]

    no_wait = events_for(0.0)
    with_wait = events_for(2.0)

    assert len(no_wait) == len(with_wait) == 20

    # Non-vacuity: the run must actually reach the degraded/fallback band,
    # otherwise no wait could have occurred and the clock check proves nothing.
    assert any(e["controller_state"] == ControllerState.PQC_FALLBACK.value for e in with_wait), (
        "cell never reached the bounded-wait band; this test would be vacuous"
    )

    no_wait_ts = [e["timestamp"] for e in no_wait]
    with_wait_ts = [e["timestamp"] for e in with_wait]

    assert with_wait_ts[-1] > no_wait_ts[-1], (
        "a configured bounded wait must advance the SimPy clock; "
        f"got {with_wait_ts[-1]} vs {no_wait_ts[-1]}"
    )

    # The clock must advance by whole wait intervals, one per waiting
    # transaction -- not by some unrelated amount.
    #
    # `timestamp` is recorded BEFORE `env.timeout()` (the harness's
    # pre-existing convention: a timestamp is the transaction's *start*
    # time, which is why the inter-transaction gap is likewise absent from
    # a transaction's own timestamp). A transaction's own wait therefore
    # shows up in the NEXT transaction's timestamp, so the last
    # transaction's wait is not reflected in the last timestamp. The wait
    # is still charged in full to that transaction's key_establishment_ms.
    n_waits_before_last = sum(
        1 for e in with_wait[:-1] if e["controller_state"] == ControllerState.PQC_FALLBACK.value
    )
    assert with_wait_ts[-1] == pytest.approx(
        no_wait_ts[-1] + 2.0 * n_waits_before_last, rel=1e-6
    )

    # And the wait must be charged to measured key-establishment latency.
    waited_events = [
        e for e in with_wait if e["controller_state"] == ControllerState.PQC_FALLBACK.value
    ]
    assert all(e["key_establishment_ms"] >= 2000.0 for e in waited_events), (
        "a 2-second bounded wait must appear in key_establishment_ms"
    )
