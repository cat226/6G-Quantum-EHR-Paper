#!/usr/bin/env python3
"""
Task 8 Phase 17 — Implementation Validation.

Runs all 8 required checks in order and reports pass/fail for each.
Exits nonzero if any CRITICAL check fails (per Phase 17: "Do NOT begin
the full experiment if any critical test fails.").
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RESULTS = []


def check(name: str, fn):
    try:
        fn()
        RESULTS.append((name, "PASS", None))
        print(f"[PASS] {name}")
    except Exception as e:
        RESULTS.append((name, "FAIL", str(e)))
        print(f"[FAIL] {name}: {e}")


# 1. Smoke test -- can every module be imported and instantiated?
def smoke_test():
    from src.crypto import classical, pqc, qkd, hybrid, authentication
    from src.adaptive import controller
    from src.baselines import baselines
    from src.network import topology, channel, edge
    from src.workload import ehr_generator
    from src.simulation import simulator, events
    from src.metrics import collector, aggregator
    from src.utils import config, random as rnd, logging as lg

    # instantiate one of each core object
    qkd.QKDPool(qkd.QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=10))
    hybrid.HKDFHybridCombiner()
    controller.AdaptiveController(
        controller.AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.01)
    )
    ehr_generator.SyntheticFHIRLikeGenerator(seed=1)
    topology.Topology.build()


check("1. Smoke test (all modules import and instantiate)", smoke_test)


# 2 & 3. Unit + integration test suite
def run_pytest():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=str(Path(__file__).resolve().parent.parent),
        capture_output=True,
        text=True,
    )
    RESULTS.append(("pytest_output", "INFO", result.stdout[-4000:]))
    if result.returncode != 0:
        raise RuntimeError(f"pytest failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}")


check("2+3. Full unit + integration test suite (pytest)", run_pytest)


# 4. Single end-to-end EHR transaction
def single_e2e_transaction():
    from src.simulation.simulator import run_cell, CellConfig
    from src.baselines.baselines import BaselineID
    from src.workload.ehr_generator import PayloadClass
    from src.adaptive.controller import AdaptiveController, AdaptiveThresholds

    def factory():
        return AdaptiveController(AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.01))

    cfg = CellConfig(
        experiment_id="validation-single-e2e",
        baseline_id=BaselineID.B5_ADAPTIVE,
        qkd_availability_config=1.0,
        device_count=1,
        payload_class=PayloadClass.MEDIUM,
        network_load="nominal",
        seed=1,
        n_transactions_per_device=1,
        sim_duration_seconds=2.0,
    )
    path = run_cell(cfg, "/tmp/phase17_validation", factory)
    import json

    with open(path) as f:
        events = [json.loads(l) for l in f]
    assert len(events) == 1, f"expected exactly 1 transaction, got {len(events)}"
    assert events[0]["success"] is True


check("4. Single end-to-end EHR transaction", single_e2e_transaction)


# 5. Single transaction for every baseline
def single_transaction_every_baseline():
    from src.baselines.baselines import BaselineID, build_baseline
    from src.adaptive.controller import AdaptiveController, AdaptiveThresholds, Criticality
    from src.crypto.qkd import QKDPool, QKDPoolConfig

    pool = QKDPool(QKDPoolConfig(capacity_bits=100_000, generation_rate_bits_per_sec=1000))
    context = {"qkd_pool": pool, "context_label": b"phase17-allbaselines", "criticality": Criticality.ROUTINE}
    controller = AdaptiveController(AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.01))

    for bid in BaselineID:
        b = build_baseline(bid, controller if bid == BaselineID.B5_ADAPTIVE else None)
        result = b.establish_session_key(context)
        assert result.success, f"{bid.value} failed unexpectedly: {result.failure_reason}"
        b.close()


check("5. Single transaction for every baseline (B1-B5)", single_transaction_every_baseline)


# 6. One forced QKD outage
def forced_outage():
    from src.crypto.qkd import QKDPool, QKDPoolConfig, QKDInsufficientMaterial

    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=100))
    pool.set_outage(True)
    pool.tick(100.0)  # would normally generate a lot; outage suppresses it
    assert pool.level_bits == 1000  # unchanged: started full, outage prevents regen but no draws yet
    pool.draw(1000)
    try:
        pool.draw(1)
        raise AssertionError("expected QKDInsufficientMaterial")
    except QKDInsufficientMaterial:
        pass


check("6. Forced QKD outage (pool depleted under outage)", forced_outage)


# 7. One forced fallback
def forced_fallback():
    from src.baselines.baselines import BaselineID, build_baseline
    from src.adaptive.controller import AdaptiveController, AdaptiveThresholds, Criticality
    from src.crypto.qkd import QKDPool, QKDPoolConfig
    from src.crypto.interfaces import KeySource

    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0))
    pool.set_outage(True)
    pool.draw(999)
    controller = AdaptiveController(AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.001))
    b5 = build_baseline(BaselineID.B5_ADAPTIVE, controller)
    result = b5.establish_session_key(
        {"qkd_pool": pool, "context_label": b"phase17-fallback", "criticality": Criticality.ROUTINE}
    )
    assert result.success is True
    assert result.key.source == KeySource.PQC_ONLY
    b5.close()


check("7. Forced fallback (B5 under outage -> PQC_ONLY)", forced_fallback)


# 8. Reproducibility check using the same seed
def reproducibility_check():
    from src.simulation.simulator import run_cell, CellConfig
    from src.baselines.baselines import BaselineID
    from src.workload.ehr_generator import PayloadClass
    from src.adaptive.controller import AdaptiveController, AdaptiveThresholds
    import json

    def factory():
        return AdaptiveController(AdaptiveThresholds(pool_min_hybrid=0.3, pool_min_wait=0.1, wait_timeout_seconds=0.05))

    def run(outdir):
        cfg = CellConfig(
            experiment_id="validation-repro",
            baseline_id=BaselineID.B5_ADAPTIVE,
            qkd_availability_config=0.5,
            device_count=5,
            payload_class=PayloadClass.LARGE,
            network_load="congested",
            seed=555,
            n_transactions_per_device=5,
            sim_duration_seconds=5.0,
        )
        return run_cell(cfg, outdir, factory)

    pa = run("/tmp/phase17_validation/repro_a")
    pb = run("/tmp/phase17_validation/repro_b")
    with open(pa) as f:
        a = [json.loads(l) for l in f]
    with open(pb) as f:
        b = [json.loads(l) for l in f]
    assert len(a) == len(b)
    fields = ["transaction_id", "payload_bytes", "mode_used", "controller_state", "success"]
    for ea, eb in zip(a, b):
        for fld in fields:
            assert ea[fld] == eb[fld], f"mismatch on {fld}: {ea[fld]} vs {eb[fld]}"


check("8. Reproducibility check (same seed, twice)", reproducibility_check)


print("\n=== SUMMARY ===")
critical_failures = [r for r in RESULTS if r[1] == "FAIL"]
for name, status, detail in RESULTS:
    if status in ("PASS", "FAIL"):
        print(f"{status}: {name}")
print(f"\n{len(RESULTS) - len(critical_failures) - 1} passed, {len(critical_failures)} failed")
sys.exit(1 if critical_failures else 0)
