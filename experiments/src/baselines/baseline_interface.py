from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class BaselineResult:
    """
    Standardized result for a baseline transaction execution.
    """
    success: bool
    selected_mode: str
    failure_reason: Optional[str] = None
    key_establishment_latency_ms: float = 0.0
    authentication_latency_ms: float = 0.0
    encryption_latency_ms: float = 0.0
    total_crypto_latency_ms: float = 0.0
    payload_bytes: int = 0
    message_overhead_bytes: int = 0

class BaselineProtocol(ABC):
    """
    Common abstraction for all five baselines (B1-B5).
    """
    
    @abstractmethod
    def initialize(self, seed: int, **kwargs):
        """
        Initializes the baseline state deterministically using a seed.
        """
        pass
        
    @abstractmethod
    def execute_transaction(self, payload: bytes, qkd_pool: Any = None) -> BaselineResult:
        """
        Executes a complete transaction pipeline including key establishment,
        authentication, and encryption.
        
        Args:
            payload: Synthetic EHR payload to transmit
            qkd_pool: Reference to the QKD pool if applicable to the baseline
            
        Returns:
            BaselineResult containing metadata and timings.
        """
        pass
