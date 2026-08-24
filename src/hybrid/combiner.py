import struct
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

def canonical_encode(k_qkd: bytes, k_pqc: bytes) -> bytes:
    """
    Encodes the two symmetric keys into an unambiguous canonical representation.

    Format:
    [4 bytes length of K_QKD] || [K_QKD] || [4 bytes length of K_PQC] || [K_PQC]
    """
    if not isinstance(k_qkd, bytes) or not isinstance(k_pqc, bytes):
        raise TypeError("Inputs must be bytes.")
    if len(k_qkd) == 0 or len(k_pqc) == 0:
        raise ValueError("Inputs cannot be empty.")

    encoded = struct.pack(">I", len(k_qkd)) + k_qkd + struct.pack(">I", len(k_pqc)) + k_pqc
    return encoded


def combine(
    k_qkd: bytes,
    k_pqc: bytes,
    key_length: int = 32,
    context: str = "6G-Quantum-EHR-Paper/hybrid-key-establishment/v1"
) -> bytes:
    """
    Combines QKD and PQC keys into a single hybrid key using HKDF-SHA256.

    Args:
        k_qkd: QKD secret key bytes
        k_pqc: ML-KEM shared secret bytes
        key_length: Desired output key length in bytes
        context: Domain separation context string

    Returns:
        Derived hybrid symmetric key
    """
    # 1. Canonical encoding to prevent ambiguity attacks
    key_material = canonical_encode(k_qkd, k_pqc)

    # 2. Derive via HKDF-SHA256
    # Note on salt: We use `None` (which defaults to a zeroed salt of hash length)
    # because the inputs K_QKD and K_PQC already provide the necessary entropy
    # and uniqueness. A separate fixed or random salt is not required for this
    # specific baseline protocol combination.
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=None,
        info=context.encode("utf-8")
    )

    k_hybrid = hkdf.derive(key_material)
    return k_hybrid
