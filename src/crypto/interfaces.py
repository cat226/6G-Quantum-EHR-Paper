from abc import ABC, abstractmethod
from enum import Enum

class SecurityMode(Enum):
    PQC_ONLY = 'PQC_ONLY'
    QKD_ONLY = 'QKD_ONLY'
    HYBRID = 'HYBRID'

class ISecurityMechanism(ABC):
    @abstractmethod
    def establish_key(self, source: str, destination: str) -> bool:
        pass

    @abstractmethod
    def get_availability_status(self) -> str:
        pass

    @abstractmethod
    def estimate_overhead_bytes(self) -> int:
        pass

    @abstractmethod
    def get_security_mode_id(self) -> SecurityMode:
        pass
