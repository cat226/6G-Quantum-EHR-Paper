from dataclasses import dataclass
from typing import Optional

@dataclass
class PQCAvailabilityModel:
    success: bool
    establishment_overhead_bytes: int
    latency_ms: float
    failure_reason: Optional[str] = None

    def __post_init__(self):
        if self.establishment_overhead_bytes < 0:
            raise ValueError('Overhead cannot be negative')
        if self.latency_ms < 0:
            raise ValueError('Latency cannot be negative')
