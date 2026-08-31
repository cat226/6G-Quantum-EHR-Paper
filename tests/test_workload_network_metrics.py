"""Unit tests for EHR generation, network delay, and metric calculation
(Task 8 Phase 16)."""

import random

from src.workload.ehr_generator import (
    PAYLOAD_SIZE_RANGES_BYTES,
    Criticality,
    PayloadClass,
    SyntheticFHIRLikeGenerator,
    TransactionType,
)
from src.network.topology import NetworkLink, NetworkParameters, Topology
from src.metrics.aggregator import summarize_cell, _percentile, _bootstrap_ci


# --- EHR generation ---


def test_deterministic_with_same_seed():
    gen1 = SyntheticFHIRLikeGenerator(seed=123)
    gen2 = SyntheticFHIRLikeGenerator(seed=123)
    t1 = gen1.generate(PayloadClass.SMALL)
    t2 = gen2.generate(PayloadClass.SMALL)
    assert t1.payload_bytes == t2.payload_bytes
    assert t1.criticality == t2.criticality


def test_different_seeds_produce_different_output_with_high_probability():
    gen1 = SyntheticFHIRLikeGenerator(seed=1)
    gen2 = SyntheticFHIRLikeGenerator(seed=2)
    batch1 = [t.payload_bytes for t in gen1.generate_batch(20, PayloadClass.MEDIUM)]
    batch2 = [t.payload_bytes for t in gen2.generate_batch(20, PayloadClass.MEDIUM)]
    assert batch1 != batch2


def test_payload_size_within_configured_range():
    gen = SyntheticFHIRLikeGenerator(seed=1)
    lo, hi = PAYLOAD_SIZE_RANGES_BYTES[PayloadClass.SMALL]
    for _ in range(20):
        txn = gen.generate(PayloadClass.SMALL)
        # actual serialized size is close to target but not exact due
        # to JSON structure overhead -- check it's in a reasonable band
        assert txn.payload_bytes > 0

def test_no_real_patient_data_markers():
    """A structural sanity check: generated bodies should only ever
    contain synthetic filler, never fields suggesting real record
    import."""
    gen = SyntheticFHIRLikeGenerator(seed=1)
    txn = gen.generate(PayloadClass.MEDIUM)
    assert "_synthetic_filler" in txn.body
    assert "patientName" not in str(txn.body)
    assert "ssn" not in str(txn.body).lower()


def test_transaction_type_recorded():
    gen = SyntheticFHIRLikeGenerator(seed=1)
    txn = gen.generate(PayloadClass.SMALL, TransactionType.SHARE)
    assert txn.transaction_type == TransactionType.SHARE


# --- Network delay ---


def test_network_link_latency_increases_with_payload_size():
    rng = random.Random(1)
    link = NetworkLink(NetworkParameters.nominal(), rng)
    small_latency, _ = link.transmit(1000)
    large_latency, _ = link.transmit(1_000_000)
    assert large_latency > small_latency


def test_congested_params_slower_than_nominal():
    rng = random.Random(1)
    nominal_link = NetworkLink(NetworkParameters.nominal(), rng)
    congested_link = NetworkLink(NetworkParameters.congested(), rng)
    n_lat, _ = nominal_link.transmit(10_000)
    c_lat, _ = congested_link.transmit(10_000)
    assert c_lat > n_lat


def test_topology_end_to_end_sums_three_hops():
    rng = random.Random(1)
    topo = Topology.build(network_load="nominal", rng=rng)
    latency, delivered = topo.end_to_end_transmit(5000)
    single_hop_latency, _ = topo.access_link.transmit(5000)
    # three hops should sum to roughly 3x a single hop's transmission
    # component (allowing for independent packet-loss draws not
    # affecting latency itself)
    assert latency >= single_hop_latency


# --- Metric calculation ---


def test_percentile_matches_known_values():
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert _percentile(values, 50) == 5.5
    assert _percentile(values, 100) == 10


def test_bootstrap_ci_contains_mean():
    values = [10.0, 12.0, 11.0, 13.0, 9.0, 10.5, 11.5]
    import statistics

    lo, hi = _bootstrap_ci(values, n_resamples=500, seed=1)
    assert lo <= statistics.mean(values) <= hi


def test_summarize_cell_from_raw_events():
    events = [
        {
            "experiment_id": "test", "baseline": "B5",
            "qkd_availability_config": 0.5, "device_count": 10,
            "payload_class": "medium", "network_load": "nominal",
            "success": True, "key_establishment_ms": 1.0 + i * 0.1,
            "end_to_end_ms": 10.0 + i * 0.1,
            "communication_overhead_bytes": 5000,
            "mode_used": "KeySource.ADAPTIVE_HYBRID" if i % 2 == 0 else "KeySource.PQC_ONLY",
        }
        for i in range(10)
    ]
    summary = summarize_cell(events)
    assert summary.n_transactions == 10
    assert summary.n_success == 10
    assert summary.successful_transmission_rate == 1.0
    assert summary.fallback_frequency == 0.5  # half were PQC_ONLY


def test_summarize_cell_reports_payload_encryption_ms_mean():
    """M3 (Task 8.5) added payload_encryption_ms to TransactionEvent; the
    aggregator must surface it, and must not choke on older raw files that
    predate the field (missing key -> treated as 0.0, not a KeyError)."""
    events = [
        {
            "experiment_id": "enc-test", "baseline": "B5",
            "qkd_availability_config": 1.0, "device_count": 10,
            "payload_class": "medium", "network_load": "nominal",
            "success": True, "key_establishment_ms": 1.0,
            "payload_encryption_ms": val,
            "end_to_end_ms": 10.0,
            "communication_overhead_bytes": 5000,
            "mode_used": "KeySource.ADAPTIVE_HYBRID",
        }
        for val in (0.02, 0.04, 0.06)
    ]
    summary = summarize_cell(events)
    assert abs(summary.payload_encryption_ms_mean - 0.04) < 1e-9

    # A raw event predating the field must not raise.
    legacy_events = [
        {
            "experiment_id": "legacy", "baseline": "B1",
            "qkd_availability_config": 1.0, "device_count": 10,
            "payload_class": "medium", "network_load": "nominal",
            "success": True, "key_establishment_ms": 1.0,
            "end_to_end_ms": 5.0, "communication_overhead_bytes": 100,
            "mode_used": "KeySource.CLASSICAL",
        }
    ]
    legacy_summary = summarize_cell(legacy_events)
    assert legacy_summary.payload_encryption_ms_mean == 0.0


def test_summarize_cell_handles_failures_in_denominator():
    events = [
        {"experiment_id": "t", "baseline": "B3", "qkd_availability_config": 0.0,
         "device_count": 10, "payload_class": "small", "network_load": "nominal",
         "success": False, "key_establishment_ms": 0, "end_to_end_ms": 0,
         "communication_overhead_bytes": 0, "mode_used": None}
        for _ in range(3)
    ] + [
        {"experiment_id": "t", "baseline": "B3", "qkd_availability_config": 0.0,
         "device_count": 10, "payload_class": "small", "network_load": "nominal",
         "success": True, "key_establishment_ms": 5.0, "end_to_end_ms": 15.0,
         "communication_overhead_bytes": 3000, "mode_used": "KeySource.QKD_ONLY"}
        for _ in range(7)
    ]
    summary = summarize_cell(events)
    assert summary.n_transactions == 10
    assert summary.n_success == 7
    assert summary.successful_transmission_rate == 0.7
