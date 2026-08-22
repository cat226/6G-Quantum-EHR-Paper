"""
The five baselines (Task 6 Section 11, Task 7 Part 6, Task 8 Phase 12).

All five expose the SAME interface (`establish_session_key`) -- the
structural fairness mechanism discussed throughout this project (Task 6
Section 19.3, Task 7 Part 6/9). They differ only in key
establishment/mode logic, never in AEAD construction, payload framing,
or logging.

Critical distinction (Task 8 Phase 12's explicit warning), preserved
here in code:
  - B3 (QKD-only): fails outright if QKD is unavailable. No fallback.
  - B4 (static hybrid): ALWAYS attempts the hybrid construction. If QKD
    is unavailable, it FAILS -- it does not silently behave like B5.
  - B5 (adaptive hybrid): uses the AdaptiveController to choose HYBRID
    or PQC_ONLY per session.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

from ..adaptive.controller import AdaptiveController, Criticality as ControllerCriticality, Mode
from ..crypto.authentication import ModularAuthenticator
from ..crypto.classical import AESGCMEncryption, ClassicalKeyEstablishment
from ..crypto.hybrid import derive_hybrid_session_key
from ..crypto.interfaces import EstablishedKey, EstablishmentFailure, KeySource
from ..crypto.pqc import MLKEMKeyEstablishment
from ..crypto.qkd import QKDInsufficientMaterial, QKDPool


class BaselineID(str, Enum):
    B1_CLASSICAL = "B1"
    B2_PQC_ONLY = "B2"
    B3_QKD_ONLY = "B3"
    B4_STATIC_HYBRID = "B4"
    B5_ADAPTIVE = "B5"


#: Bits of QKD material drawn per session when QKD contributes to the
#: key. Fixed at 256 bits (matches the AES-256 key length this project
#: standardizes on) -- an internally-derived parameter (Task 7 Part 3),
#: not a QKD-literature figure.
QKD_BITS_PER_SESSION = 256


@dataclass
class SessionResult:
    """What every baseline's establish_session_key() returns -- a
    single, uniform result shape across all five baselines, so the
    metrics collector doesn't need per-baseline special-casing."""

    baseline: BaselineID
    success: bool
    key: EstablishedKey | None
    total_establishment_ms: float
    message_count: int
    total_bytes: int
    controller_state: str | None = None  # only meaningful for B5
    failure_reason: str | None = None


class Baseline:
    """Shared scaffolding all five baselines build on. Not itself one
    of the five -- each concrete baseline below overrides
    establish_session_key()."""

    id: BaselineID

    def __init__(self):
        self._authenticator = ModularAuthenticator(use_pqc=self.id != BaselineID.B1_CLASSICAL)
        self.aead = AESGCMEncryption()

    def _authenticate_round_trip(self, message: bytes) -> tuple[float, int]:
        """Sign + verify one message (e.g., the mode-sync handshake or
        classical-channel authentication, Task 6 Section 3/5). Returns
        (total_ms, message_bytes) -- used identically by every baseline
        that authenticates, keeping this cost comparable across them
        (Task 7 Part 6's fairness audit)."""
        result = self._authenticator.sign(message)
        verification = self._authenticator.verify(message, result.signature)
        if not verification.valid:
            raise EstablishmentFailure("authentication self-check failed")
        return result.sign_ms + verification.verify_ms, len(result.signature)

    def establish_session_key(self, context: dict) -> SessionResult:
        raise NotImplementedError

    def close(self):
        self._authenticator.close()


class B1Classical(Baseline):
    """Pre-quantum reference point (Task 6 Section 11). X25519 + Ed25519."""

    id = BaselineID.B1_CLASSICAL

    def __init__(self):
        super().__init__()
        self._kex = ClassicalKeyEstablishment()

    def establish_session_key(self, context: dict) -> SessionResult:
        t0 = time.perf_counter()
        try:
            key = self._kex.establish(context)
            auth_ms, auth_bytes = self._authenticate_round_trip(b"session-establish:B1")
        except Exception as e:
            return SessionResult(
                baseline=self.id, success=False, key=None,
                total_establishment_ms=(time.perf_counter() - t0) * 1000,
                message_count=0, total_bytes=0, failure_reason=str(e),
            )
        t1 = time.perf_counter()
        return SessionResult(
            baseline=self.id, success=True, key=key,
            total_establishment_ms=(t1 - t0) * 1000,
            message_count=key.metadata["message_count"] + 1,
            total_bytes=key.metadata["public_key_bytes"] + auth_bytes,
        )


class B2PQCOnly(Baseline):
    """ML-KEM-768 + ML-DSA-65 + AES-256-GCM (Task 6 Section 11)."""

    id = BaselineID.B2_PQC_ONLY

    def __init__(self):
        super().__init__()
        self._kex = MLKEMKeyEstablishment()

    def establish_session_key(self, context: dict) -> SessionResult:
        t0 = time.perf_counter()
        try:
            key = self._kex.establish(context)
            auth_ms, auth_bytes = self._authenticate_round_trip(b"session-establish:B2")
        except Exception as e:
            return SessionResult(
                baseline=self.id, success=False, key=None,
                total_establishment_ms=(time.perf_counter() - t0) * 1000,
                message_count=0, total_bytes=0, failure_reason=str(e),
            )
        t1 = time.perf_counter()
        return SessionResult(
            baseline=self.id, success=True, key=key,
            total_establishment_ms=(t1 - t0) * 1000,
            message_count=key.metadata["message_count"] + 1,
            total_bytes=(
                key.metadata["public_key_bytes"] + key.metadata["ciphertext_bytes"] + auth_bytes
            ),
        )


class B3QKDOnly(Baseline):
    """QKD-only (Task 6 Section 11 / Task 7 Part 6's resolution): the
    classical control channel IS authenticated with ML-DSA (same
    mechanism as the proposed system) -- "QKD-only" refers to the
    session-key material only, not the full authentication stack
    (Task 7 Part 6's explicit resolution of this open question)."""

    id = BaselineID.B3_QKD_ONLY

    def establish_session_key(self, context: dict) -> SessionResult:
        pool: QKDPool = context["qkd_pool"]
        t0 = time.perf_counter()
        try:
            qkd_secret = pool.draw(QKD_BITS_PER_SESSION)
            auth_ms, auth_bytes = self._authenticate_round_trip(b"session-establish:B3")
        except QKDInsufficientMaterial as e:
            # No fallback -- this IS the unmitigated-outage comparison
            # point (Task 6 Section 11).
            return SessionResult(
                baseline=self.id, success=False, key=None,
                total_establishment_ms=(time.perf_counter() - t0) * 1000,
                message_count=0, total_bytes=0, failure_reason=str(e),
            )
        t1 = time.perf_counter()
        key = EstablishedKey(
            key_material=qkd_secret, source=KeySource.QKD_ONLY,
            metadata={"qkd_bits": QKD_BITS_PER_SESSION},
        )
        return SessionResult(
            baseline=self.id, success=True, key=key,
            total_establishment_ms=(t1 - t0) * 1000,
            message_count=1 + 1,  # QKD sifting exchange (modeled abstractly, 1) + auth
            total_bytes=auth_bytes,
        )


class B4StaticHybrid(Baseline):
    """Always attempts QKD + ML-KEM combined via HKDF. Blocks/fails on
    QKD unavailability -- resolved explicitly in Task 7 Part 6 to keep
    B4 behaviorally distinct from B5 under outage. Does NOT behave like
    B5 (Task 8 Phase 12's explicit warning)."""

    id = BaselineID.B4_STATIC_HYBRID

    def __init__(self):
        super().__init__()
        self._pqc_kex = MLKEMKeyEstablishment()

    def establish_session_key(self, context: dict) -> SessionResult:
        pool: QKDPool = context["qkd_pool"]
        t0 = time.perf_counter()
        try:
            qkd_secret = pool.draw(QKD_BITS_PER_SESSION)
            pqc_key = self._pqc_kex.establish(context)
            session_key_bytes = derive_hybrid_session_key(
                qkd_secret, pqc_key.key_material, context.get("context_label", b"B4"), 32
            )
            auth_ms, auth_bytes = self._authenticate_round_trip(b"session-establish:B4")
        except (QKDInsufficientMaterial, EstablishmentFailure) as e:
            # Explicit, resolved behavior (Task 7 Part 6): block/fail,
            # do not fall back.
            return SessionResult(
                baseline=self.id, success=False, key=None,
                total_establishment_ms=(time.perf_counter() - t0) * 1000,
                message_count=0, total_bytes=0, failure_reason=str(e),
            )
        t1 = time.perf_counter()
        key = EstablishedKey(
            key_material=session_key_bytes, source=KeySource.STATIC_HYBRID,
            metadata={**pqc_key.metadata, "qkd_bits": QKD_BITS_PER_SESSION},
        )
        return SessionResult(
            baseline=self.id, success=True, key=key,
            total_establishment_ms=(t1 - t0) * 1000,
            message_count=pqc_key.metadata["message_count"] + 1 + 1,  # PQC msgs + QKD exchange + auth
            total_bytes=(
                pqc_key.metadata["public_key_bytes"]
                + pqc_key.metadata["ciphertext_bytes"]
                + auth_bytes
            ),
        )


class B5Adaptive(Baseline):
    """Chooses HYBRID (B4's path) or PQC_ONLY (B2's path) per session
    via the AdaptiveController (Task 6 Section 4). Adds the mode-sync
    handshake cost on top of whichever path is chosen (Task 6 Section
    3/Task 7 Part 6's communication-messages analysis)."""

    id = BaselineID.B5_ADAPTIVE

    def __init__(self, controller: AdaptiveController):
        super().__init__()
        self._controller = controller
        self._pqc_kex = MLKEMKeyEstablishment()

    def establish_session_key(self, context: dict) -> SessionResult:
        pool: QKDPool = context["qkd_pool"]
        criticality = context.get("criticality", ControllerCriticality.ROUTINE)
        t0 = time.perf_counter()

        decision = self._controller.select_mode(pool, criticality)

        try:
            # Mode-sync handshake: authenticated announcement of the
            # chosen mode, on top of whichever establishment path
            # follows (Task 6 Section 3 step 6).
            mode_sync_ms, mode_sync_bytes = self._authenticate_round_trip(
                f"mode-sync:{decision.mode.value}".encode()
            )

            if decision.mode == Mode.HYBRID:
                qkd_secret = pool.draw(QKD_BITS_PER_SESSION)
                pqc_key = self._pqc_kex.establish(context)
                session_key_bytes = derive_hybrid_session_key(
                    qkd_secret, pqc_key.key_material, context.get("context_label", b"B5"), 32
                )
                source = KeySource.ADAPTIVE_HYBRID
                msg_count = pqc_key.metadata["message_count"] + 1  # + QKD exchange
                establishment_bytes = (
                    pqc_key.metadata["public_key_bytes"] + pqc_key.metadata["ciphertext_bytes"]
                )
                extra_meta = {**pqc_key.metadata, "qkd_bits": QKD_BITS_PER_SESSION}
            else:
                pqc_key = self._pqc_kex.establish(context)
                session_key_bytes = pqc_key.key_material
                source = KeySource.PQC_ONLY
                msg_count = pqc_key.metadata["message_count"]
                establishment_bytes = (
                    pqc_key.metadata["public_key_bytes"] + pqc_key.metadata["ciphertext_bytes"]
                )
                extra_meta = pqc_key.metadata

            auth_ms, auth_bytes = self._authenticate_round_trip(b"session-establish:B5")
        except (QKDInsufficientMaterial, EstablishmentFailure) as e:
            return SessionResult(
                baseline=self.id, success=False, key=None,
                total_establishment_ms=(time.perf_counter() - t0) * 1000,
                message_count=0, total_bytes=0,
                controller_state=decision.state.value, failure_reason=str(e),
            )

        t1 = time.perf_counter()
        key = EstablishedKey(key_material=session_key_bytes, source=source, metadata=extra_meta)
        return SessionResult(
            baseline=self.id, success=True, key=key,
            total_establishment_ms=(t1 - t0) * 1000,
            message_count=msg_count + 2,  # + mode-sync + session auth
            total_bytes=establishment_bytes + mode_sync_bytes + auth_bytes,
            controller_state=decision.state.value,
        )


def build_baseline(baseline_id: BaselineID, controller: AdaptiveController | None = None) -> Baseline:
    """Factory -- ensures every baseline is constructed uniformly by
    the simulation harness rather than harness code branching on
    baseline-specific constructors."""
    if baseline_id == BaselineID.B1_CLASSICAL:
        return B1Classical()
    if baseline_id == BaselineID.B2_PQC_ONLY:
        return B2PQCOnly()
    if baseline_id == BaselineID.B3_QKD_ONLY:
        return B3QKDOnly()
    if baseline_id == BaselineID.B4_STATIC_HYBRID:
        return B4StaticHybrid()
    if baseline_id == BaselineID.B5_ADAPTIVE:
        if controller is None:
            raise ValueError("B5 requires an AdaptiveController instance")
        return B5Adaptive(controller)
    raise ValueError(f"unknown baseline id: {baseline_id}")
