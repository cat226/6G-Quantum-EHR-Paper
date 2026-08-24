import time
from typing import Tuple
from src.hybrid.key_establishment import establish_hybrid_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class HybridKDF:
    """
    Adapter for the Task 6 hybrid construction.
    Reuses the existing implementation to ensure we don't invent a second combiner.
    """
    @staticmethod
    def derive_hybrid_key(k_qkd: bytes, k_pqc: bytes, context: str = "6G-Quantum-EHR-Paper/hybrid-key-establishment/v1") -> Tuple[bytes, float]:
        start = time.perf_counter()
        k_hybrid, _ = establish_hybrid_key(k_qkd=k_qkd, k_pqc=k_pqc, context=context)
        end = time.perf_counter()
        return k_hybrid, (end - start) * 1000.0

class ClassicalKDF:
    """
    KDF for the classical baseline (X25519 shared secret to AES key).
    """
    @staticmethod
    def derive_key(shared_secret: bytes, salt: bytes = None, length: int = 32) -> Tuple[bytes, float]:
        start = time.perf_counter()
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=b"6G-Quantum-EHR-Paper/classical-baseline/v1"
        )
        key = hkdf.derive(shared_secret)
        end = time.perf_counter()
        return key, (end - start) * 1000.0
