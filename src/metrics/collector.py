from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SecurityMetrics:
    security_mode: str
    key_establishment_success: bool
    qkd_availability_state: str
    fallback_event_triggered: bool

@dataclass
class PerformanceMetrics:
    key_establishment_latency_ms: float
    ehr_transmission_latency_ms: float
    communication_overhead_bytes: int
    processing_overhead_ms: Optional[float] = None

    def __post_init__(self):
        if self.key_establishment_latency_ms < 0:
            raise ValueError('Latency cannot be negative')
        if self.ehr_transmission_latency_ms < 0:
            raise ValueError('Latency cannot be negative')
        if self.communication_overhead_bytes < 0:
            raise ValueError('Overhead cannot be negative')
        if self.processing_overhead_ms is not None and self.processing_overhead_ms < 0:
            raise ValueError('Processing overhead cannot be negative')

@dataclass
class ScalabilityMetrics:
    concurrent_sessions: int
    total_ehr_transmissions: int
    network_load_percent: float
    key_material_demand_bits: int

    def __post_init__(self):
        if self.concurrent_sessions < 0:
            raise ValueError('Concurrent sessions cannot be negative')
        if self.total_ehr_transmissions < 0:
            raise ValueError('Total EHR transmissions cannot be negative')
        if not (0.0 <= self.network_load_percent <= 100.0):
            raise ValueError('Network load must be between 0 and 100')
        if self.key_material_demand_bits < 0:
            raise ValueError('Key material demand cannot be negative')

class MetricsCollector:
    def __init__(self):
        self.security_metrics: List[SecurityMetrics] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.scalability_metrics: List[ScalabilityMetrics] = []

    def record_security_metric(self, metric: SecurityMetrics) -> None:
        self.security_metrics.append(metric)

    def record_performance_metric(self, metric: PerformanceMetrics) -> None:
        self.performance_metrics.append(metric)

    def record_scalability_metric(self, metric: ScalabilityMetrics) -> None:
        self.scalability_metrics.append(metric)
