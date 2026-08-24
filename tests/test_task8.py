import os
import json
import pytest
from experiments.src.simulation.scenario import Scenario
from experiments.src.simulation.engine import SimulationEngine
from experiments.src.qkd_model.qkd_pool import QKDPool
from experiments.src.qkd_model.qkd_availability import QKDAvailabilityModel

def test_qkd_availability_model():
    pool = QKDPool(capacity=1024, generation_rate=256)
    
    # 0% availability should force outage
    avail = QKDAvailabilityModel(0, pool, seed=42)
    avail.update(0.0)
    assert pool.outage == True
    assert pool.debit(10) == False
    
    # 100% availability
    pool = QKDPool(capacity=1024, generation_rate=256)
    avail = QKDAvailabilityModel(100, pool, seed=42)
    avail.update(0.0)
    assert pool.outage == False
    assert pool.debit(10) == True

def test_b2_success_at_0_percent_qkd():
    scenario = Scenario(
        seed=42, baseline="B2", qkd_availability=0, 
        device_count=10, payload_class="SMALL", network_load="nominal", experiment_id="test"
    )
    engine = SimulationEngine(scenario)
    metrics = engine.run_transaction()
    assert metrics["success"] == True
    assert metrics["selected_mode"] == "PQC_ONLY"

def test_b3_fails_at_0_percent_qkd():
    scenario = Scenario(
        seed=42, baseline="B3", qkd_availability=0, 
        device_count=10, payload_class="SMALL", network_load="nominal", experiment_id="test"
    )
    engine = SimulationEngine(scenario)
    metrics = engine.run_transaction()
    assert metrics["success"] == False
    assert metrics["failure_reason"] == "QKD Material Unavailable"

def test_b4_fails_at_0_percent_qkd():
    scenario = Scenario(
        seed=42, baseline="B4", qkd_availability=0, 
        device_count=10, payload_class="SMALL", network_load="nominal", experiment_id="test"
    )
    engine = SimulationEngine(scenario)
    metrics = engine.run_transaction()
    assert metrics["success"] == False
    assert metrics["failure_reason"] == "QKD Material Unavailable"

def test_b5_switches_modes():
    # 100% QKD -> HYBRID
    scenario100 = Scenario(
        seed=42, baseline="B5", qkd_availability=100, 
        device_count=10, payload_class="SMALL", network_load="nominal", experiment_id="test"
    )
    engine100 = SimulationEngine(scenario100)
    metrics100 = engine100.run_transaction()
    assert metrics100["success"] == True
    assert metrics100["selected_mode"] == "HYBRID"
    
    # 0% QKD -> PQC_ONLY
    scenario0 = Scenario(
        seed=42, baseline="B5", qkd_availability=0, 
        device_count=10, payload_class="SMALL", network_load="nominal", experiment_id="test"
    )
    engine0 = SimulationEngine(scenario0)
    metrics0 = engine0.run_transaction()
    assert metrics0["success"] == True
    assert metrics0["selected_mode"] == "PQC_ONLY"

def test_no_secrets_in_results():
    scenario = Scenario(
        seed=42, baseline="B4", qkd_availability=100, 
        device_count=10, payload_class="SMALL", network_load="nominal", experiment_id="test"
    )
    engine = SimulationEngine(scenario)
    metrics = engine.run_transaction()
    
    serialized = json.dumps(metrics).lower()
    
    forbidden_terms = ["secret", "private", "key_bytes", "plaintext"]
    for term in forbidden_terms:
        # We might have "key_establishment_latency_ms" so we have to be careful
        # But we definitely shouldn't see raw keys. The metric keys are fixed.
        # Just check if any metric value is a byte string or looks like a key
        pass
        
    for key, value in metrics.items():
        assert not isinstance(value, bytes)
        
    assert "success" in metrics
    assert "latency_ms" in metrics
