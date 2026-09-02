"""
A simplified, explicitly-labeled 6G-relevant network abstraction (Task 6
Section 9, Task 7 Part 5, Task 8 Phase 10). NOT a complete 6G stack --
no PHY/MAC layer, no real radio protocol, no claim of reproducing a
finalized 6G standard.

Topology modeled: EHR client/IoMT -> 6G access abstraction -> edge
gateway -> hospital network -> EHR server (exactly the chain specified
in Task 8 Phase 10).
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class NetworkParameters:
    """All values are simulation assumptions -- see
    docs/implementation_notes.md's Part-5-derived table for the
    current/future-target/simplification breakdown behind each of
    these. None of these values represents a finalized 6G standard.
    """

    propagation_delay_ms: float
    processing_delay_ms: float
    transmission_rate_mbps: float
    packet_loss_probability: float
    edge_processing_delay_ms: float

    @classmethod
    def nominal(cls) -> "NetworkParameters":
        return cls(
            propagation_delay_ms=2.0,
            processing_delay_ms=1.0,
            transmission_rate_mbps=500.0,
            packet_loss_probability=0.001,
            edge_processing_delay_ms=0.5,
        )

    @classmethod
    def congested(cls) -> "NetworkParameters":
        return cls(
            propagation_delay_ms=8.0,
            processing_delay_ms=4.0,
            transmission_rate_mbps=100.0,
            packet_loss_probability=0.02,
            edge_processing_delay_ms=2.0,
        )


class NetworkLink:
    """One hop in the EHR client -> ... -> EHR server chain.

    `transmit(payload_bytes)` returns (latency_ms, delivered: bool).
    Packet loss is modeled as a per-attempt probability, not a queueing
    simulation of retransmission -- kept simple deliberately, per Task 6
    Section 9's "simplified research abstraction containing only the
    characteristics needed for our experiment."
    """

    def __init__(self, params: NetworkParameters, rng: random.Random | None = None):
        self.params = params
        self._rng = rng or random.Random()

    def transmit(self, payload_bytes: int) -> tuple[float, bool]:
        transmission_ms = (payload_bytes * 8) / (self.params.transmission_rate_mbps * 1000)
        latency_ms = (
            self.params.propagation_delay_ms
            + self.params.processing_delay_ms
            + transmission_ms
        )
        delivered = self._rng.random() >= self.params.packet_loss_probability
        return latency_ms, delivered


@dataclass
class Topology:
    """EHR client/IoMT -> 6G access -> edge gateway -> hospital network
    -> EHR server (Task 8 Phase 10's exact chain)."""

    access_link: NetworkLink       # client/IoMT <-> 6G access abstraction
    edge_link: NetworkLink         # 6G access <-> edge gateway
    backbone_link: NetworkLink     # edge gateway <-> hospital network / EHR server

    @classmethod
    def build(cls, network_load: str = "nominal", rng: random.Random | None = None) -> "Topology":
        params = NetworkParameters.nominal() if network_load == "nominal" else NetworkParameters.congested()
        return cls(
            access_link=NetworkLink(params, rng),
            edge_link=NetworkLink(params, rng),
            backbone_link=NetworkLink(params, rng),
        )

    def end_to_end_transmit(self, payload_bytes: int) -> tuple[float, bool]:
        """Sum latency and delivery across all three hops. A single
        dropped hop fails the whole transaction -- no retry logic is
        modeled at this layer (retries, if any, are a baseline/adaptive
        concern per Task 6 Section 4/6, not a network-layer concern)."""
        total_ms = 0.0
        for link in (self.access_link, self.edge_link, self.backbone_link):
            ms, delivered = link.transmit(payload_bytes)
            total_ms += ms
            if not delivered:
                return total_ms, False
        return total_ms, True
