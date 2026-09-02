"""
Discrete-event simulation core (Task 6 Section 17's tool recommendation,
Task 8 Phase 2). Uses SimPy to orchestrate device/client transaction
arrivals for one experiment cell.

A "cell" is one specific (baseline, QKD availability, device count,
payload class, network load) combination -- the unit Task 6 Section 13
and Task 7 Part 7 define the pilot/full matrix in terms of.
"""

from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass

import simpy

from ..adaptive.controller import Criticality
from ..baselines.baselines import Baseline, BaselineID
from ..crypto.qkd import QKDPool
from ..metrics.collector import MetricsCollector, TransactionEvent
from ..network.topology import Topology
from ..workload.ehr_generator import PayloadClass, SyntheticFHIRLikeGenerator, TransactionType


@dataclass
class CellConfig:
    experiment_id: str
    baseline_id: BaselineID
    qkd_availability_config: float  # nominal fraction, e.g. 1.0, 0.5, 0.0
    device_count: int
    payload_class: PayloadClass
    network_load: str  # "nominal" | "congested"
    seed: int
    n_transactions_per_device: int = 1
    sim_duration_seconds: float = 10.0  # simulated wall-clock window


def _qkd_generation_rate_for_availability(availability_fraction: float, capacity_bits: int) -> float:
    """Maps the *configured nominal availability* (Task 6/7's
    experimental-design lever, e.g. "50%") to a QKD pool generation
    rate. MODELED ASSUMPTION (Task 7 Part 3 / Task 7.1 Section 7): there
    is no literature-measured "the" mapping from a percentage label to
    a bits/sec rate -- this is a deliberately simple, documented
    modeling choice, revised once already during implementation
    validation (see docs/implementation_notes.md, "QKD pool calibration
    finding"): an earlier version anchored the full-availability rate to
    "regenerate the whole pool in ~2 seconds," which combined with a
    large pool (sized independent of session draw size) meant the pool
    never drained at moderate load within a short simulated window --
    the availability parameter had no visible effect. Anchoring the
    full-availability rate to "regenerate the whole pool in ~1 second"
    AND sizing the pool relative to a session's draw (see
    build_qkd_pool_config below) makes the parameter responsive at
    realistic device counts. At availability=0.0, generation is exactly
    zero -- the pool can only drain (Task 6 Section 6). Intermediate
    values scale linearly between these two anchors; this linear
    scaling itself is flagged as a SENSITIVITY VARIABLE (Task 7 Part 3),
    not asserted as how real QKD channel degradation behaves."""
    full_rate = capacity_bits / 1.0
    return full_rate * availability_fraction


def build_qkd_pool_config(availability_fraction: float, sessions_buffer: int = 20):
    """Sizes the pool relative to a session's key draw (Task 6 Section
    6: "the pool holds N sessions' worth of key material at full
    charge") rather than an arbitrary large constant -- this is the
    fix for the calibration finding above. `sessions_buffer=20` is
    itself a MODELED ASSUMPTION / SENSITIVITY VARIABLE, not a literature
    figure; see Task 7 Part 10's canonical parameter table."""
    from ..baselines.baselines import QKD_BITS_PER_SESSION
    from ..crypto.qkd import QKDPoolConfig

    capacity_bits = QKD_BITS_PER_SESSION * sessions_buffer
    return QKDPoolConfig(
        capacity_bits=capacity_bits,
        generation_rate_bits_per_sec=_qkd_generation_rate_for_availability(
            availability_fraction, capacity_bits
        ),
    )


def run_cell(config: CellConfig, output_dir: str, controller_factory) -> str:
    """Runs one experiment cell to completion, writing raw
    TransactionEvent records to `{output_dir}/{experiment_id}.jsonl`.
    Returns the output file path.

    `controller_factory()` builds a fresh AdaptiveController (only used
    when baseline_id == B5) -- injected so this module doesn't need to
    import AdaptiveThresholds directly, keeping it decoupled from the
    specific threshold values a given config chooses.
    """
    from pathlib import Path

    output_path = Path(output_dir) / f"{config.experiment_id}.jsonl"

    pool_capacity_bits = 8_000_000  # superseded below; kept only as a fallback constant
    from ..crypto.qkd import QKDPoolConfig

    qkd_pool_cfg = build_qkd_pool_config(config.qkd_availability_config, sessions_buffer=20)
    qkd_pool = QKDPool(qkd_pool_cfg)

    topology = Topology.build(network_load=config.network_load, rng=random.Random(config.seed + 1))
    workload_gen = SyntheticFHIRLikeGenerator(seed=config.seed)

    baseline: Baseline
    from ..baselines.baselines import build_baseline

    controller = controller_factory() if config.baseline_id == BaselineID.B5_ADAPTIVE else None
    baseline = build_baseline(config.baseline_id, controller)

    env = simpy.Environment()
    collector = MetricsCollector(output_path)

    def device_process(env: simpy.Environment, device_id: int):
        for _ in range(config.n_transactions_per_device):
            txn = workload_gen.generate(config.payload_class, TransactionType.SHARE)
            criticality = (
                Criticality.EMERGENCY
                if txn.criticality.value == "emergency"
                else Criticality.ROUTINE
            )
            context = {
                "qkd_pool": qkd_pool,
                "context_label": f"{config.experiment_id}-{txn.transaction_id}".encode(),
                "criticality": criticality,
            }

            wall_t0 = time.perf_counter()
            result = baseline.establish_session_key(context)

            if result.success:
                # Use the derived session key to actually encrypt the EHR
                # payload with AES-256-GCM, then decrypt it (round trip,
                # matching the pattern _authenticate_round_trip already
                # uses for signatures) -- every baseline shares this same
                # AEAD instance (self.aead), so this cost is identical
                # across B1-B5 and differs only in which key established
                # it. What is transmitted over the network is the
                # ciphertext (payload + 12-byte nonce + 16-byte GCM tag),
                # not the raw plaintext size.
                plaintext = str(txn.body).encode("utf-8")
                enc_t0 = time.perf_counter()
                ciphertext = baseline.aead.encrypt(
                    result.key.key_material, plaintext, context["context_label"]
                )
                baseline.aead.decrypt(
                    result.key.key_material, ciphertext, context["context_label"]
                )
                enc_t1 = time.perf_counter()
                payload_encryption_ms = (enc_t1 - enc_t0) * 1000

                net_latency_ms, delivered = topology.end_to_end_transmit(len(ciphertext))
                success = delivered
            else:
                payload_encryption_ms = 0.0
                net_latency_ms, delivered = 0.0, False
                success = False

            wall_t1 = time.perf_counter()

            # The controller's bounded wait already advanced the QKD
            # pool's clock inside establish_session_key(). Charge that
            # same interval to key-establishment latency and to SimPy
            # below, so the pool, the clock, and the metrics agree.
            wait_ms = result.wait_seconds * 1000.0

            mode_used = str(result.key.source) if result.key else None
            collector.record(
                TransactionEvent(
                    timestamp=env.now,
                    experiment_id=config.experiment_id,
                    baseline=config.baseline_id.value,
                    qkd_availability_config=config.qkd_availability_config,
                    device_count=config.device_count,
                    payload_class=config.payload_class.value,
                    network_load=config.network_load,
                    seed=config.seed,
                    transaction_id=txn.transaction_id,
                    success=success,
                    key_establishment_ms=result.total_establishment_ms + wait_ms,
                    payload_encryption_ms=payload_encryption_ms,
                    network_latency_ms=net_latency_ms,
                    end_to_end_ms=(
                        result.total_establishment_ms
                        + wait_ms
                        + payload_encryption_ms
                        + net_latency_ms
                    ),
                    communication_overhead_bytes=result.total_bytes,
                    payload_bytes=txn.payload_bytes,
                    mode_used=mode_used,
                    controller_state=result.controller_state,
                    failure_reason=result.failure_reason,
                )
            )
            # Advance simulated time to represent a small gap between a
            # device's transactions; QKD pool regenerates during this
            # gap via tick(), driven by the elapsed simulated seconds.
            gap = 0.05
            qkd_pool.tick(gap)
            # Advance SimPy by the inter-transaction gap PLUS any bounded
            # wait the controller performed. The pool was already ticked
            # for the wait interval inside establish_session_key(), so it
            # is not ticked for it again here -- pool time and env time
            # advance by the same total.
            yield env.timeout(gap + result.wait_seconds)

    for device_id in range(config.device_count):
        env.process(device_process(env, device_id))

    env.run(until=config.sim_duration_seconds)

    collector.close()
    baseline.close()
    return str(output_path)
