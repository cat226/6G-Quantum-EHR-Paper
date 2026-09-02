"""Unit tests for the modular authentication component (Task 8 Phase 16)."""

from src.crypto.authentication import ModularAuthenticator


def test_pqc_authenticator_sign_verify_roundtrip():
    auth = ModularAuthenticator(use_pqc=True)
    result = auth.sign(b"mode-sync: HYBRID")
    verification = auth.verify(b"mode-sync: HYBRID", result.signature)
    assert verification.valid is True
    auth.close()


def test_classical_authenticator_sign_verify_roundtrip():
    auth = ModularAuthenticator(use_pqc=False)
    result = auth.sign(b"session-establish:B1")
    verification = auth.verify(b"session-establish:B1", result.signature)
    assert verification.valid is True


def test_timings_are_recorded_and_nonnegative():
    auth = ModularAuthenticator(use_pqc=True)
    result = auth.sign(b"msg")
    verification = auth.verify(b"msg", result.signature)
    assert result.sign_ms >= 0
    assert verification.verify_ms >= 0
    auth.close()
