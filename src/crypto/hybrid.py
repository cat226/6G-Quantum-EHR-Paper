"""
The hybrid QKD+PQC key combiner, exactly as resolved in Task 7.1:

    IKM = QKD_secret || ML-KEM_secret
    PRK = HKDF-Extract(salt, IKM)
    session_key = HKDF-Expand(PRK, info, L)

SECURITY CLAIM (Task 7.1 Section 8, Claim C -- restated here so it
travels with the code, not just the docs):

    "An engineering-level key combination using HKDF to derive a
    session key from independently generated QKD and ML-KEM secrets."

This is explicitly NOT claimed to be a formally proven compositional
combiner for this exact QKD+PQC case (Task 7.1 Section 2's finding:
KEM-specific combiner proofs do not automatically transfer to an input
that is not a KEM output, which QKD-derived material is not). Do not
strengthen this claim elsewhere in the codebase or the paper without
re-running Task 7.1's verification.
"""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .interfaces import SessionKeyDerivation

#: Security claim string, reused verbatim wherever this construction's
#: security property needs to be stated (code comments, logs, the
#: eventual paper) so it can't silently drift into an overclaim.
SECURITY_CLAIM = (
    "Engineering-level key combination using HKDF to derive a session "
    "key from independently generated QKD and ML-KEM secrets. No "
    "compositional security proof is claimed for this specific "
    "QKD+PQC instantiation (Task 7.1)."
)


class HKDFHybridCombiner(SessionKeyDerivation):
    """B4/B5's session-key derivation (Task 7.1's resolved construction).

    `context_label` is bound in as HKDF's `info` parameter, not
    concatenated into the raw input keying material -- this was the
    specific correction Task 7.1 made to the original draft design
    (context belongs in info/salt, not IKM).
    """

    def __init__(self, hash_algorithm=None):
        self._hash_algorithm = hash_algorithm or hashes.SHA256()

    def derive(self, secrets: list[bytes], context_label: bytes, length: int) -> bytes:
        if len(secrets) < 1:
            raise ValueError("at least one secret is required")
        ikm = b"".join(secrets)
        hkdf = HKDF(
            algorithm=self._hash_algorithm,
            length=length,
            salt=None,  # no independent salt source modeled; documented in
            # docs/implementation_notes.md as a simplification --
            # HKDF is defined to work correctly with salt=None
            # (RFC 5869 treats absent salt as a string of zeros).
            info=context_label,
        )
        return hkdf.derive(ikm)


def derive_hybrid_session_key(
    qkd_secret: bytes,
    ml_kem_secret: bytes,
    context_label: bytes,
    length: int = 32,
) -> bytes:
    """Convenience wrapper implementing the exact construction from
    Task 7.1: IKM = QKD || ML-KEM, then HKDF-Extract-then-Expand with
    context_label as `info`."""
    combiner = HKDFHybridCombiner()
    return combiner.derive([qkd_secret, ml_kem_secret], context_label, length)
