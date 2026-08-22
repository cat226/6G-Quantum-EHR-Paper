"""
Modular authentication component (Task 8 Phase 8).

Wraps ClassicalAuthentication (Ed25519, B1 only) and MLDSAAuthentication
(ML-DSA-65, B2-B5) behind a uniform call shape so the simulation harness
and baselines don't need to know which underlying mechanism is in use.

Per Task 8 Phase 8's explicit instruction: this module authenticates
classical/control traffic and application/session establishment
messages. It does NOT claim to authenticate the physical quantum
channel -- QKD's own physical-layer properties are what protect that
(Task 7.1 Section 5). This is documented here, not just in prose
elsewhere, because it's easy for this distinction to get lost once code
exists.
"""

from __future__ import annotations

from dataclasses import dataclass

from .classical import ClassicalAuthentication
from .pqc import MLDSAAuthentication


@dataclass
class AuthenticationResult:
    signature: bytes
    signer_public_key: bytes
    sign_ms: float


@dataclass
class VerificationResult:
    valid: bool
    verify_ms: float


class ModularAuthenticator:
    """A single authenticator instance backing either Ed25519 (B1) or
    ML-DSA-65 (B2-B5), selected at construction time.

    SIMULATION ASSUMPTION (Task 8 Phase 8, restated): both the classical
    QKD/control traffic and the application/session establishment
    messages are modeled as authenticated by this component. Real QKD
    deployments authenticate the classical channel as part of the QKD
    protocol's own reconciliation process; this simulation does not
    model that process's internals (Task 8 Phase 6) and instead applies
    the same authenticator uniformly to both classical-control and
    application-session messages, as a simplification.
    """

    def __init__(self, use_pqc: bool = True):
        self._use_pqc = use_pqc
        self._backend = MLDSAAuthentication() if use_pqc else ClassicalAuthentication()

    @property
    def public_key_bytes(self) -> bytes:
        if self._use_pqc:
            return self._backend.public_key_bytes
        return self._backend.public_key_bytes

    def sign(self, message: bytes) -> AuthenticationResult:
        sig, ms = self._backend.sign_timed(message)
        return AuthenticationResult(
            signature=sig, signer_public_key=self.public_key_bytes, sign_ms=ms
        )

    def verify(self, message: bytes, signature: bytes) -> VerificationResult:
        ok, ms = self._backend.verify_timed(message, signature)
        return VerificationResult(valid=ok, verify_ms=ms)

    def close(self):
        if self._use_pqc:
            self._backend.close()
