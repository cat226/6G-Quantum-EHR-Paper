from typing import Tuple, Optional
from src.hybrid.base import HybridResult
from src.hybrid.combiner import combine

def establish_hybrid_key(
    k_qkd: Optional[bytes],
    k_pqc: Optional[bytes],
    key_length: int = 32,
    context: str = "6G-Quantum-EHR-Paper/hybrid-key-establishment/v1"
) -> Tuple[bytes, HybridResult]:
    """
    Coordinates the final hybrid key establishment.

    Args:
        k_qkd: The QKD key material
        k_pqc: The ML-KEM shared secret
        key_length: The requested output key length
        context: Domain separation context

    Returns:
        Tuple[bytes, HybridResult]: The derived hybrid key and associated metadata.
    """
    if k_qkd is None or k_pqc is None:
        raise ValueError("Both QKD and ML-KEM keys are mandatory. Fallback is not permitted.")

    if not isinstance(k_qkd, bytes) or not isinstance(k_pqc, bytes):
        raise TypeError("Key material must be bytes.")

    if len(k_qkd) == 0 or len(k_pqc) == 0:
        raise ValueError("Key material cannot be empty.")

    k_hybrid = combine(
        k_qkd=k_qkd,
        k_pqc=k_pqc,
        key_length=key_length,
        context=context
    )

    metadata = HybridResult(
        key_length=key_length,
        context=context
    )

    return k_hybrid, metadata
