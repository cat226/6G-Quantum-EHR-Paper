import pytest
import yaml
from pathlib import Path
from src.simulation.models import Entity, EntityRole, NetworkCondition, EHRTransmission
from src.crypto.interfaces import SecurityMode, ISecurityMechanism
from src.qkd.availability import QKDAvailabilityState
from src.crypto.pqc_availability import PQCAvailabilityModel
from src.crypto.hybrid_strategies import HybridStrategy
from src.metrics.collector import SecurityMetrics, PerformanceMetrics, ScalabilityMetrics, MetricsCollector

def test_ehr_transmission():
    # valid EHRTransmission creation
    valid_ehr = EHRTransmission('tx1', 'src1', 'dst1', 1024, 1, 'HYBRID')
    assert valid_ehr.payload_size_bytes == 1024

    # invalid/negative payload size
    with pytest.raises(ValueError, match='positive'):
        EHRTransmission('tx1', 'src1', 'dst1', 0, 1, 'HYBRID')
    with pytest.raises(ValueError, match='positive'):
        EHRTransmission('tx1', 'src1', 'dst1', -5, 1, 'HYBRID')

    # negative timestamp_sequence
    with pytest.raises(ValueError, match='negative'):
        EHRTransmission('tx1', 'src1', 'dst1', 100, -1, 'HYBRID')

def test_network_condition():
    # valid NetworkCondition
    valid_net = NetworkCondition(10.0, 100.0, 0.05, 0.1, 5.0, 'AVAILABLE', True)
    assert valid_net.propagation_latency_ms == 10.0

    # negative latency rejected
    with pytest.raises(ValueError, match='negative'):
        NetworkCondition(-1.0, 100.0, 0.05, 0.1, 5.0, 'AVAILABLE', True)

    # negative bandwidth rejected
    with pytest.raises(ValueError, match='negative'):
        NetworkCondition(10.0, -10.0, 0.05, 0.1, 5.0, 'AVAILABLE', True)

    # packet loss outside 0..1 rejected
    with pytest.raises(ValueError, match='between 0 and 1'):
        NetworkCondition(10.0, 100.0, -0.1, 0.1, 5.0, 'AVAILABLE', True)
    with pytest.raises(ValueError, match='between 0 and 1'):
        NetworkCondition(10.0, 100.0, 1.1, 0.1, 5.0, 'AVAILABLE', True)

    # negative congestion rejected
    with pytest.raises(ValueError, match='negative'):
        NetworkCondition(10.0, 100.0, 0.05, -0.1, 5.0, 'AVAILABLE', True)

    # negative edge-processing delay rejected
    with pytest.raises(ValueError, match='negative'):
        NetworkCondition(10.0, 100.0, 0.05, 0.1, -5.0, 'AVAILABLE', True)

def test_security_abstractions():
    # enums exist
    assert SecurityMode.PQC_ONLY.value == 'PQC_ONLY'
    assert SecurityMode.QKD_ONLY.value == 'QKD_ONLY'
    assert SecurityMode.HYBRID.value == 'HYBRID'

    # ISecurityMechanism is abstract
    with pytest.raises(TypeError):
        ISecurityMechanism()

def test_qkd_availability():
    assert QKDAvailabilityState.AVAILABLE.value == 'AVAILABLE'
    assert QKDAvailabilityState.UNAVAILABLE.value == 'UNAVAILABLE'
    assert QKDAvailabilityState.INSUFFICIENT_KEY_MATERIAL.value == 'INSUFFICIENT_KEY_MATERIAL'
    assert QKDAvailabilityState.DEGRADED.value == 'DEGRADED'

def test_pqc_availability():
    # valid PQCAvailabilityModel
    valid_pqc = PQCAvailabilityModel(True, 128, 1.5)
    assert valid_pqc.success is True

    # negative overhead rejected
    with pytest.raises(ValueError, match='negative'):
        PQCAvailabilityModel(True, -1, 1.5)

    # negative latency rejected
    with pytest.raises(ValueError, match='negative'):
        PQCAvailabilityModel(True, 128, -1.5)

def test_hybrid_strategies():
    assert HybridStrategy.SIMULTANEOUS_QKD_PQC.value == 'SIMULTANEOUS_QKD_PQC'
    assert HybridStrategy.PQC_DEFAULT_QKD_LAYER.value == 'PQC_DEFAULT_QKD_LAYER'
    assert HybridStrategy.QKD_PRIMARY_PQC_FALLBACK.value == 'QKD_PRIMARY_PQC_FALLBACK'
    assert HybridStrategy.ADAPTIVE_SWITCHING.value == 'ADAPTIVE_SWITCHING'

def test_metrics_collector():
    collector = MetricsCollector()

    # metrics can be recorded
    sec_metric = SecurityMetrics('HYBRID', True, 'AVAILABLE', False)
    perf_metric = PerformanceMetrics(1.5, 2.0, 1024, 0.5)
    scal_metric = ScalabilityMetrics(10, 100, 45.5, 2048)

    collector.record_security_metric(sec_metric)
    collector.record_performance_metric(perf_metric)
    collector.record_scalability_metric(scal_metric)

    assert len(collector.security_metrics) == 1
    assert len(collector.performance_metrics) == 1
    assert len(collector.scalability_metrics) == 1

    # negative PerformanceMetrics rejected
    with pytest.raises(ValueError, match='negative'):
        PerformanceMetrics(-1.0, 10.0, 100)
    with pytest.raises(ValueError, match='negative'):
        PerformanceMetrics(10.0, -1.0, 100)
    with pytest.raises(ValueError, match='negative'):
        PerformanceMetrics(10.0, 10.0, -100)
    with pytest.raises(ValueError, match='negative'):
        PerformanceMetrics(10.0, 10.0, 100, -5.0)

    # invalid ScalabilityMetrics rejected
    with pytest.raises(ValueError, match='negative'):
        ScalabilityMetrics(-1, 10, 50.0, 256)
    with pytest.raises(ValueError, match='negative'):
        ScalabilityMetrics(1, -10, 50.0, 256)
    with pytest.raises(ValueError, match='between 0 and 100'):
        ScalabilityMetrics(1, 10, 101.0, 256)
    with pytest.raises(ValueError, match='between 0 and 100'):
        ScalabilityMetrics(1, 10, -0.1, 256)
    with pytest.raises(ValueError, match='negative'):
        ScalabilityMetrics(1, 10, 50.0, -256)

def test_configuration_validation():
    config_path = Path("config/default.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    # verify experiment values
    assert config["experiment"]["seed"] is None
    assert config["experiment"]["mode"] is None
    assert config["experiment"]["number_of_sessions"] is None
    assert config["experiment"]["output_directory"] is None

    # verify network values
    assert config["network"]["latency"] is None
    assert config["network"]["bandwidth"] is None
    assert config["network"]["packet_loss"] is None

    # verify qkd values
    assert config["qkd"]["availability"] is None
    assert config["qkd"]["key_material"] is None

    # verify ehr values
    assert config["ehr"]["payload_size"] is None
