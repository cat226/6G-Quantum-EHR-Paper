import pytest

from src.hybrid import combine, establish_hybrid_key, HybridResult, canonical_encode

def test_deterministic_derivation():
    """Verify HKDF-SHA256 derivation is deterministic."""
    k_qkd = b"qkd_secret_123"
    k_pqc = b"pqc_secret_456"

    key1, _ = establish_hybrid_key(k_qkd, k_pqc)
    key2, _ = establish_hybrid_key(k_qkd, k_pqc)

    assert key1 == key2

def test_qkd_contribution():
    """Verify changing QKD input changes the hybrid key."""
    k_qkd1 = b"A" * 32
    k_qkd2 = b"C" * 32
    k_pqc = b"B" * 32

    key1 = combine(k_qkd1, k_pqc)
    key2 = combine(k_qkd2, k_pqc)

    assert key1 != key2

def test_pqc_contribution():
    """Verify changing PQC input changes the hybrid key."""
    k_qkd = b"A" * 32
    k_pqc1 = b"B" * 32
    k_pqc2 = b"C" * 32

    key1 = combine(k_qkd, k_pqc1)
    key2 = combine(k_qkd, k_pqc2)

    assert key1 != key2

def test_both_inputs_contributing():
    """Verify both inputs contribute to the output (A,B != C,D)."""
    key1 = combine(b"A"*32, b"B"*32)
    key2 = combine(b"C"*32, b"D"*32)
    assert key1 != key2

def test_input_ordering():
    """Verify that input order matters under canonical encoding."""
    # combine(A, B) != combine(B, A)
    k_qkd = b"qkd_secret"
    k_pqc = b"pqc_secret"

    assert k_qkd != k_pqc
    key1 = combine(k_qkd, k_pqc)
    key2 = combine(k_pqc, k_qkd)
    assert key1 != key2

def test_empty_qkd_rejection():
    """Verify empty QKD input is rejected."""
    with pytest.raises(ValueError, match="cannot be empty"):
        establish_hybrid_key(b"", b"pqc_secret")

def test_empty_pqc_rejection():
    """Verify empty ML-KEM input is rejected."""
    with pytest.raises(ValueError, match="cannot be empty"):
        establish_hybrid_key(b"qkd_secret", b"")

def test_invalid_input_type_rejection():
    """Verify non-bytes inputs are rejected."""
    with pytest.raises(TypeError, match="must be bytes"):
        establish_hybrid_key("not_bytes", b"pqc_secret") # type: ignore

    with pytest.raises(TypeError, match="must be bytes"):
        establish_hybrid_key(b"qkd_secret", 123) # type: ignore

def test_configured_output_length():
    """Verify the output key length matches configuration."""
    k_qkd = b"A" * 32
    k_pqc = b"B" * 32

    key_32, metadata_32 = establish_hybrid_key(k_qkd, k_pqc, key_length=32)
    assert len(key_32) == 32
    assert metadata_32.key_length == 32

    key_64, metadata_64 = establish_hybrid_key(k_qkd, k_pqc, key_length=64)
    assert len(key_64) == 64
    assert metadata_64.key_length == 64

def test_domain_separation():
    """Verify domain separation context alters output."""
    k_qkd = b"A" * 32
    k_pqc = b"B" * 32

    key1, _ = establish_hybrid_key(k_qkd, k_pqc, context="context1")
    key2, _ = establish_hybrid_key(k_qkd, k_pqc, context="context2")

    assert key1 != key2

def test_metadata_correctness():
    """Verify metadata defaults and structure."""
    _, metadata = establish_hybrid_key(b"A", b"B")

    assert isinstance(metadata, HybridResult)
    assert metadata.protocol == "hybrid-key-establishment/v1"
    assert metadata.qkd_mechanism == "BB84"
    assert metadata.pqc_mechanism == "ML-KEM"
    assert metadata.combiner == "HKDF-SHA256"

def test_secrets_absent_from_metadata():
    """Verify metadata does not leak secrets."""
    k_qkd = b"SUPER_SECRET_QKD"
    k_pqc = b"SUPER_SECRET_PQC"
    k_hybrid, metadata = establish_hybrid_key(k_qkd, k_pqc)

    metadata_repr = repr(metadata)
    assert "SUPER_SECRET" not in metadata_repr
    assert k_qkd not in metadata.__dict__.values()
    assert k_pqc not in metadata.__dict__.values()
    assert k_hybrid not in metadata.__dict__.values()

def test_both_mechanisms_required():
    """Verify fallback is prohibited (both must be present)."""
    with pytest.raises(ValueError, match="mandatory"):
        establish_hybrid_key(None, b"pqc")

    with pytest.raises(ValueError, match="mandatory"):
        establish_hybrid_key(b"qkd", None)

def test_canonical_encoding_structure():
    """Verify the encoding is unambiguous (A, BC) != (AB, C)."""
    # K_QKD=A, K_PQC=BC
    enc1 = canonical_encode(b"A", b"BC")
    # K_QKD=AB, K_PQC=C
    enc2 = canonical_encode(b"AB", b"C")

    assert enc1 != enc2

    # Check actual output of canonical_encode for lengths
    # b"A" (1 byte) -> 0x00 0x00 0x00 0x01
    assert enc1.startswith(b"\x00\x00\x00\x01A")
