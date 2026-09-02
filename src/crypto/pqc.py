"""
Post-Quantum Cryptography primitives: ML-KEM-768 (key establishment) and
ML-DSA-65 (authentication), via the real `liboqs` library (Task 7 Part
2, Task 8 Phase 5).

IMPORTANT -- per Task 8's explicit instruction: "If liboqs/Python
bindings are unavailable or problematic on the platform, do NOT
silently replace ML-KEM with an unrelated algorithm." That situation
did NOT occur in this implementation: `liboqs` was built from source in
this environment (see docs/implementation_notes.md for the exact build
steps -- a minimal build enabling only ML-KEM-768 and ML-DSA-65, since a
full build of every algorithm in liboqs was not needed and would have
cost significant build time for no benefit to this project). All sizes
and timings in this module are retrieved programmatically from the real
library at call time -- nothing here is a recalled or invented number.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import oqs

from .interfaces import (
    Authentication,
    EstablishedKey,
    EstablishmentFailure,
    KeyEstablishment,
    KeySource,
)

ML_KEM_ALG = "ML-KEM-768"
ML_DSA_ALG = "ML-DSA-65"

_available_kems = oqs.get_enabled_kem_mechanisms()
_available_sigs = oqs.get_enabled_sig_mechanisms()

if ML_KEM_ALG not in _available_kems:
    raise EstablishmentFailure(
        f"{ML_KEM_ALG} not enabled in this liboqs build. "
        f"Available KEMs: {_available_kems}. "
        "Per Task 8's instruction, this must be documented and fixed, "
        "not silently substituted with a different algorithm."
    )
if ML_DSA_ALG not in _available_sigs:
    raise EstablishmentFailure(
        f"{ML_DSA_ALG} not enabled in this liboqs build. "
        f"Available signatures: {_available_sigs}."
    )


@dataclass
class PQCKeypairInfo:
    """Sizes retrieved programmatically from liboqs -- see
    docs/implementation_notes.md Table 1 for the actual measured values
    from this environment (Task 8 Phase 5: "Do not fabricate missing
    byte sizes. Retrieve them from the actual implementation/library.")
    """

    public_key_bytes: int
    secret_key_bytes: int
    ciphertext_bytes: int | None = None  # KEM only
    shared_secret_bytes: int | None = None  # KEM only
    signature_bytes: int | None = None  # signature only


def get_ml_kem_info() -> PQCKeypairInfo:
    with oqs.KeyEncapsulation(ML_KEM_ALG) as kem:
        d = kem.details
        return PQCKeypairInfo(
            public_key_bytes=d["length_public_key"],
            secret_key_bytes=d["length_secret_key"],
            ciphertext_bytes=d["length_ciphertext"],
            shared_secret_bytes=d["length_shared_secret"],
        )


def get_ml_dsa_info() -> PQCKeypairInfo:
    with oqs.Signature(ML_DSA_ALG) as sig:
        d = sig.details
        return PQCKeypairInfo(
            public_key_bytes=d["length_public_key"],
            secret_key_bytes=d["length_secret_key"],
            signature_bytes=d["length_signature"],
        )


class MLKEMKeyEstablishment(KeyEstablishment):
    """ML-KEM-768 key encapsulation (B2's key establishment, and the
    PQC half of B4/B5's hybrid construction)."""

    def establish(self, context: dict) -> EstablishedKey:
        # A single-process simulation stands in for both sides: the
        # "receiver" generates a keypair, the "sender" encapsulates
        # against its public key, both derive the same shared secret.
        # This mirrors ClassicalKeyEstablishment's approach and keeps
        # every baseline's establish() callable in isolation for tests.
        with oqs.KeyEncapsulation(ML_KEM_ALG) as receiver:
            t0 = time.perf_counter()
            public_key = receiver.generate_keypair()
            t1 = time.perf_counter()

            with oqs.KeyEncapsulation(ML_KEM_ALG) as sender:
                ciphertext, shared_secret_sender = sender.encap_secret(public_key)
            t2 = time.perf_counter()

            shared_secret_receiver = receiver.decap_secret(ciphertext)
            t3 = time.perf_counter()

        if shared_secret_sender != shared_secret_receiver:
            # Should never happen with a correct liboqs build; caught
            # explicitly because a silent mismatch would be far worse
            # than a loud failure (Task 6 Section 4's fail-closed rule
            # for authentication/PQC failures applies here too).
            raise EstablishmentFailure(
                "ML-KEM shared secret mismatch between encap and decap -- "
                "this indicates a broken PQC implementation, not a normal "
                "failure mode. Aborting rather than silently continuing."
            )

        return EstablishedKey(
            key_material=shared_secret_receiver,
            source=KeySource.PQC_ONLY,
            metadata={
                "keygen_ms": (t1 - t0) * 1000,
                "encap_ms": (t2 - t1) * 1000,
                "decap_ms": (t3 - t2) * 1000,
                "public_key_bytes": len(public_key),
                "ciphertext_bytes": len(ciphertext),
                "shared_secret_bytes": len(shared_secret_receiver),
                "message_count": 2,  # public key + ciphertext
            },
        )


class MLDSAAuthentication(Authentication):
    """ML-DSA-65 signatures. Used for endpoint authentication and,
    per Task 6 Section 5/7 and Task 7.1 Section 5, for authenticating
    the QKD classical control channel and the mode-sync handshake --
    NOT the quantum channel itself (Task 7.1 Section 5 is explicit
    about this distinction)."""

    def __init__(self):
        self._sig = oqs.Signature(ML_DSA_ALG)
        self._public_key = self._sig.generate_keypair()

    @property
    def public_key_bytes(self) -> bytes:
        return self._public_key

    def sign(self, message: bytes) -> bytes:
        return self._sig.sign(message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        # Verification of one's own signature needs only the public key,
        # not the private-key-holding Signature object, but liboqs'
        # Python API exposes verify() as an instance method taking the
        # public key explicitly -- this works for both self- and
        # peer-verification.
        return self._sig.verify(message, signature, self._public_key)

    def verify_as(self, message: bytes, signature: bytes, signer_public_key: bytes) -> bool:
        """Verify a signature produced by a *different* party's key --
        the realistic case (Edge Gateway verifying the Hospital Server's
        signature, or vice versa)."""
        with oqs.Signature(ML_DSA_ALG) as verifier:
            return verifier.verify(message, signature, signer_public_key)

    def sign_timed(self, message: bytes) -> tuple[bytes, float]:
        t0 = time.perf_counter()
        sig = self.sign(message)
        t1 = time.perf_counter()
        return sig, (t1 - t0) * 1000

    def verify_timed(self, message: bytes, signature: bytes) -> tuple[bool, float]:
        t0 = time.perf_counter()
        ok = self.verify(message, signature)
        t1 = time.perf_counter()
        return ok, (t1 - t0) * 1000

    def close(self):
        self._sig.free()
