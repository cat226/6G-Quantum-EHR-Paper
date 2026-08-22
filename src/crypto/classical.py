"""
Classical (pre-quantum) cryptographic primitives: X25519 ECDH key
exchange, Ed25519 signatures, AES-256-GCM AEAD.

This is the B1 baseline's primitive set (Task 7 Part 2, Task 8 Phase 4).
It exists specifically to represent the "no quantum resistance"
comparison point -- it should not be made artificially weak or
artificially strong; X25519/Ed25519 are a realistic, modern deployment
choice, not a strawman.

All timing/size measurements are taken from the real `cryptography`
library at call time, never hard-coded.
"""

from __future__ import annotations

import time

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)

from .interfaces import (
    AEADEncryption,
    Authentication,
    EstablishedKey,
    EstablishmentFailure,
    KeyEstablishment,
    KeySource,
)


class ClassicalKeyEstablishment(KeyEstablishment):
    """X25519 ephemeral Diffie-Hellman key exchange (B1).

    Ephemeral-per-session, matching the forward-secrecy convention used
    for the PQC side (Task 6 Section 6 -- STANDARD TECHNIQUE, not a
    research claim).
    """

    def establish(self, context: dict) -> EstablishedKey:
        peer_public_key: X25519PublicKey | None = context.get("peer_public_key")
        if peer_public_key is None:
            # Simulate the peer side inline for a single-process simulation:
            # in the real topology this would come from the other endpoint's
            # message; here we generate both sides so the module is testable
            # standalone and so the simulation harness can call this from a
            # single event without a second live process.
            peer_private = X25519PrivateKey.generate()
            peer_public_key = peer_private.public_key()

        t0 = time.perf_counter()
        own_private = X25519PrivateKey.generate()
        own_public = own_private.public_key()
        t1 = time.perf_counter()
        shared_secret = own_private.exchange(peer_public_key)
        t2 = time.perf_counter()

        own_public_bytes = own_public.public_bytes(Encoding.Raw, PublicFormat.Raw)

        return EstablishedKey(
            key_material=shared_secret,
            source=KeySource.CLASSICAL,
            metadata={
                "keygen_ms": (t1 - t0) * 1000,
                "exchange_ms": (t2 - t1) * 1000,
                "public_key_bytes": len(own_public_bytes),
                "message_count": 1,  # one X25519 public key sent
            },
        )


class ClassicalAuthentication(Authentication):
    """Ed25519 signatures (B1's authentication mechanism)."""

    def __init__(self, private_key: Ed25519PrivateKey | None = None):
        self._private_key = private_key or Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()

    @property
    def public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

    def sign(self, message: bytes) -> bytes:
        return self._private_key.sign(message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        try:
            self._public_key.verify(signature, message)
            return True
        except Exception:
            return False

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


class AESGCMEncryption(AEADEncryption):
    """AES-256-GCM AEAD (Task 7 Part 2 -- shared across all baselines,
    per the fairness commitment in Task 6 Section 11 / Task 7 Part 6:
    baselines must differ only in key establishment, not in the AEAD
    construction used once a key is derived."""

    NONCE_BYTES = 12  # standard GCM nonce size

    def encrypt(self, key: bytes, plaintext: bytes, associated_data: bytes = b"") -> bytes:
        aesgcm = AESGCM(_derive_aes256_key(key))
        nonce = _random_nonce(self.NONCE_BYTES)
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext  # nonce prefixed so decrypt() is self-contained

    def decrypt(self, key: bytes, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
        aesgcm = AESGCM(_derive_aes256_key(key))
        nonce, actual_ciphertext = (
            ciphertext[: self.NONCE_BYTES],
            ciphertext[self.NONCE_BYTES :],
        )
        return aesgcm.decrypt(nonce, actual_ciphertext, associated_data)


def _derive_aes256_key(key_material: bytes) -> bytes:
    """AES-256-GCM needs exactly 32 bytes. Upstream key-establishment
    mechanisms may not always produce exactly 32 bytes (e.g., X25519's
    raw shared secret is 32 bytes already, but this guards the case
    generically rather than assuming it). Uses HKDF -- the same
    combiner-family primitive used elsewhere in this project (Task 7.1),
    not a new mechanism -- to size the key correctly.
    """
    if len(key_material) == 32:
        return key_material
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"aes256-gcm-key-sizing",
    ).derive(key_material)


def _random_nonce(n: int) -> bytes:
    import os

    return os.urandom(n)
