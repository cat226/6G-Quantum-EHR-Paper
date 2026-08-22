"""
Edge gateway processing model (Task 8 Phase 2/10).

Distinct from the network *transport* model (topology.py/channel.py):
this represents the Edge Gateway's own compute contribution to
end-to-end latency -- the adaptive-decision logic's execution time plus
a small fixed overhead, layered on top of (not instead of) the real,
measured crypto-operation timings that come from src/crypto/*.py.

Per Task 7 Part 5: edge processing delay is "mostly not a 6G assumption
at all" -- it's dominated by real measured crypto timings; only the
non-crypto adaptive-decision overhead here is a modeled assumption.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EdgeGatewayConfig:
    #: Non-crypto compute overhead for running the adaptive decision
    #: logic itself (Task 6 Section 4) -- deliberately small, since the
    #: decision logic is simple threshold comparisons, not heavy
    #: computation. MODELED ASSUMPTION.
    decision_overhead_ms: float = 0.05


class EdgeGateway:
    """Wraps the fixed, small adaptive-decision overhead. Real crypto
    timings are NOT modeled here -- they come from actually calling
    src/crypto/*.py, which is where the genuine cost lives."""

    def __init__(self, config: EdgeGatewayConfig | None = None):
        self.config = config or EdgeGatewayConfig()

    def decision_overhead_ms(self) -> float:
        return self.config.decision_overhead_ms
