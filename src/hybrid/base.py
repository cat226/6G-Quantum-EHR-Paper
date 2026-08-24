from dataclasses import dataclass, field
from typing import Optional

@dataclass
class HybridResult:
    """Metadata result from a hybrid key establishment process."""
    protocol: str = "hybrid-key-establishment/v1"
    qkd_mechanism: str = "BB84"
    pqc_mechanism: str = "ML-KEM"
    combiner: str = "HKDF-SHA256"
    kdf: str = "HKDF"
    key_length: int = 32
    context: str = "6G-Quantum-EHR-Paper/hybrid-key-establishment/v1"
