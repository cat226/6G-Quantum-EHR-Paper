"""
Abstract interfaces for key establishment, authentication, session key
derivation, and AEAD encryption.

Every baseline (B1-B5) implements these same interfaces (Task 8 Phase 3).
This is a structural fairness mechanism: it makes it harder for baselines
to differ in anything other than their security/key-establishment
strategy, because they are all plugged into the same simulation harness
through the same shape of object.

No cryptographic operation is implemented in this file. This file only
defines *shapes*.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class EstablishmentFailure(Exception):
    """Raised when key establishment cannot complete.

    Distinguishing this from a generic exception matters: Task 6's
    failure-handling design requires that a failed establishment produce
    a *failed transaction*, never a silent downgrade to a weaker or
    unencrypted mode (Task 6 Section 4/6). Callers must catch this
    specifically and record a failure, not retry with a different,
    unrequested mechanism.
    """


class KeySource(str, Enum):
    """Which mechanism(s) actually contributed to a derived session key.

    Recorded on every EstablishedKey so the metrics collector can verify
    -- from real logs, not from what the config *intended* -- which mode
    was actually used for every session. This is the concrete check
    Task 6 Section 19.3 and Task 7 Part 7 flagged: "does the system
    genuinely behave adaptively, or does it only look adaptive."
    """

    CLASSICAL = "classical"          # B1
    PQC_ONLY = "pqc_only"            # B2, and B5 in PQC_FALLBACK mode
    QKD_ONLY = "qkd_only"            # B3
    STATIC_HYBRID = "static_hybrid"  # B4
    ADAPTIVE_HYBRID = "adaptive_hybrid"  # B5 in HYBRID mode


@dataclass
class EstablishedKey:
    """The result of a successful key establishment.

    `key_material` is the raw derived symmetric key (bytes), ready to be
    used directly as an AEAD key. `source` records which mechanism(s)
    produced it (KeySource). `metadata` carries everything the metrics
    collector needs without re-deriving it: message/byte counts,
    per-operation timings, etc. Keeping metadata generic (dict) rather
    than a rigid schema lets each baseline report what is actually
    relevant to it without forcing irrelevant fields onto others.
    """

    key_material: bytes
    source: KeySource
    metadata: dict = field(default_factory=dict)


class KeyEstablishment(ABC):
    """Establishes a session key between two simulated endpoints.

    Implementations: classical ECDH (B1), ML-KEM (B2), QKD-pool draw
    (B3), QKD+ML-KEM combined (B4), or adaptive selection between the
    PQC-only and combined paths (B5, via the adaptive controller).
    """

    @abstractmethod
    def establish(self, context: dict) -> EstablishedKey:
        """Run key establishment for one session.

        `context` carries whatever the implementation needs (e.g., a
        reference to the QKD pool, a session/transaction id for context
        binding). Raises EstablishmentFailure on failure -- never
        returns a degraded-but-successful result silently.
        """
        raise NotImplementedError


class Authentication(ABC):
    """Authenticates a party or a message exchange.

    Used both for endpoint authentication (EHR client/server, IoMT
    device) and for authenticating the QKD classical control channel
    (Task 6 Section 5/7, Task 7.1 Section 5). The same interface serves
    both uses; *what* is being authenticated is a caller concern, not an
    interface concern.
    """

    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def verify(self, message: bytes, signature: bytes) -> bool:
        raise NotImplementedError


class SessionKeyDerivation(ABC):
    """Combines one or more secrets into a final session key.

    For B1/B2/B3 this is typically a passthrough or a simple KDF over a
    single secret. For B4/B5 (hybrid modes) this is the HKDF combiner
    from Task 7/7.1: `HKDF-Expand(HKDF-Extract(salt, secret_a ||
    secret_b), info, L)`, explicitly under Task 7.1's Claim C (an
    engineering-level combination, no compositional security proof
    claimed for combining a QKD-derived secret with an ML-KEM secret --
    see docs/implementation_notes.md).
    """

    @abstractmethod
    def derive(self, secrets: list[bytes], context_label: bytes, length: int) -> bytes:
        raise NotImplementedError


class AEADEncryption(ABC):
    """Encrypts/decrypts payloads under a derived session key."""

    @abstractmethod
    def encrypt(self, key: bytes, plaintext: bytes, associated_data: bytes = b"") -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, key: bytes, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
        raise NotImplementedError
