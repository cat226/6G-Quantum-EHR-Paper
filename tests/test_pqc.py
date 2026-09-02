"""Unit tests for ML-KEM/ML-DSA operations (Task 8 Phase 16)."""

import oqs
import pytest

from src.crypto.interfaces import EstablishmentFailure
from src.crypto.pqc import (
    ML_DSA_ALG,
    ML_KEM_ALG,
    MLDSAAuthentication,
    MLKEMKeyEstablishment,
    get_ml_dsa_info,
    get_ml_kem_info,
)


def test_ml_kem_roundtrip_produces_matching_secret():
    result = MLKEMKeyEstablishment().establish({})
    assert len(result.key_material) == 32  # ML-KEM-768's shared secret length


def test_ml_kem_shared_secret_mismatch_raises(monkeypatch):
    """Exercises the fail-loud guard in pqc.py directly: a real mismatch
    between encap and decap never occurs against a correct liboqs build,
    but the guard exists specifically for the case where it does (a
    broken build), and that code path is real code that must itself be
    tested, not merely present. Forces the condition by monkeypatching
    decap_secret to return a corrupted secret, then asserts establish()
    raises EstablishmentFailure rather than silently returning the wrong
    key -- silently continuing here would be far worse than a loud
    failure (Task 6 Section 4's fail-closed rule for PQC failures)."""
    real_decap_secret = oqs.KeyEncapsulation.decap_secret

    def corrupting_decap_secret(self, ciphertext):
        real_secret = real_decap_secret(self, ciphertext)
        return bytes(b ^ 0xFF for b in real_secret)

    monkeypatch.setattr(oqs.KeyEncapsulation, "decap_secret", corrupting_decap_secret)

    with pytest.raises(EstablishmentFailure, match="shared secret mismatch"):
        MLKEMKeyEstablishment().establish({})


def test_ml_kem_sizes_match_library_reported_values():
    """Task 8 Phase 5: sizes retrieved programmatically, not fabricated."""
    info = get_ml_kem_info()
    assert info.public_key_bytes > 0
    assert info.ciphertext_bytes > 0
    assert info.shared_secret_bytes == 32


def test_ml_dsa_sign_and_verify():
    auth = MLDSAAuthentication()
    msg = b"test message"
    sig = auth.sign(msg)
    assert auth.verify(msg, sig) is True
    auth.close()


def test_ml_dsa_rejects_tampered_message():
    auth = MLDSAAuthentication()
    msg = b"original message"
    sig = auth.sign(msg)
    assert auth.verify(b"tampered message", sig) is False
    auth.close()


def test_ml_dsa_rejects_tampered_signature():
    auth = MLDSAAuthentication()
    msg = b"a message"
    sig = auth.sign(msg)
    tampered_sig = bytes([sig[0] ^ 0xFF]) + sig[1:]
    assert auth.verify(msg, tampered_sig) is False
    auth.close()


def test_ml_dsa_sizes_match_library_reported_values():
    info = get_ml_dsa_info()
    assert info.public_key_bytes > 0
    assert info.signature_bytes > 0


def test_algorithm_names_are_the_intended_standards():
    """Confirms no silent substitution occurred (Task 8's explicit
    instruction about liboqs unavailability)."""
    assert ML_KEM_ALG == "ML-KEM-768"
    assert ML_DSA_ALG == "ML-DSA-65"
