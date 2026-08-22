"""
Synthetic EHR workload generator (Task 6 Section 10, Task 7 Part 4,
Task 8 Phase 9). No real patient data anywhere in this module.

Payload size ranges are MODELED ASSUMPTIONS, loosely anchored to general
FHIR-resource-size familiarity (Task 7 Part 4) -- explicitly NOT
literature-measured facts. See docs/implementation_notes.md.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class PayloadClass(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class TransactionType(str, Enum):
    READ = "read"
    WRITE = "write"
    SHARE = "share"  # the type most literally matching "EHR sharing" (Task 6 Section 10)


class Criticality(str, Enum):
    ROUTINE = "routine"
    EMERGENCY = "emergency"


#: (min_bytes, max_bytes) per class -- MODELED ASSUMPTION, Task 7 Part 4.
PAYLOAD_SIZE_RANGES_BYTES: dict[PayloadClass, tuple[int, int]] = {
    PayloadClass.SMALL: (1_000, 5_000),
    PayloadClass.MEDIUM: (20_000, 80_000),
    PayloadClass.LARGE: (200_000, 1_000_000),
}

#: Default emergency-transaction rate within a realistic mix.
#: MODELED ASSUMPTION -- not a sweep axis per Task 6/7's modification #1
#: (criticality is secondary/optional, not a primary independent
#: variable).
DEFAULT_EMERGENCY_FRACTION = 0.05


@dataclass
class EHRTransaction:
    transaction_id: str
    payload_class: PayloadClass
    payload_bytes: int
    transaction_type: TransactionType
    criticality: Criticality
    #: A FHIR-inspired synthetic body -- structure only, never real data.
    body: dict


class SyntheticFHIRLikeGenerator:
    """Generates FHIR-*inspired* synthetic records -- not a claim of
    FHIR standard conformance (Task 6 Section 10 is explicit that
    conformance isn't the point; representative structure/size is).

    Deterministic when given a seed (Task 8 Phase 9's explicit
    requirement), via a private random.Random instance rather than the
    global random module -- so multiple generators can run
    independently within one process without interfering with each
    other's sequences.
    """

    def __init__(
        self,
        seed: int | None = None,
        emergency_fraction: float = DEFAULT_EMERGENCY_FRACTION,
        payload_ranges: dict[PayloadClass, tuple[int, int]] | None = None,
    ):
        self._rng = random.Random(seed)
        self._emergency_fraction = emergency_fraction
        self._ranges = payload_ranges or PAYLOAD_SIZE_RANGES_BYTES
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"txn-{self._counter:08d}"

    def _synthetic_body(self, payload_class: PayloadClass, target_bytes: int) -> dict:
        """A structurally FHIR-Bundle-like nested dict, padded with a
        synthetic filler field to reach approximately target_bytes when
        serialized -- the point is a controllable, repeatable payload
        size, not literal FHIR-schema validity."""
        base = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Observation",
                        "status": "final",
                        "code": {"text": "synthetic-vital-sign"},
                        "valueQuantity": {"value": self._rng.uniform(50, 150), "unit": "bpm"},
                    }
                }
            ],
        }
        # Pad to approximately the target size with a synthetic,
        # clearly-labeled filler string (never real content).
        overhead = len(str(base))
        filler_len = max(0, target_bytes - overhead)
        base["_synthetic_filler"] = "x" * filler_len
        return base

    def generate(
        self,
        payload_class: PayloadClass,
        transaction_type: TransactionType = TransactionType.SHARE,
    ) -> EHRTransaction:
        lo, hi = self._ranges[payload_class]
        target_bytes = self._rng.randint(lo, hi)
        body = self._synthetic_body(payload_class, target_bytes)
        criticality = (
            Criticality.EMERGENCY
            if self._rng.random() < self._emergency_fraction
            else Criticality.ROUTINE
        )
        actual_bytes = len(str(body).encode("utf-8"))
        return EHRTransaction(
            transaction_id=self._next_id(),
            payload_class=payload_class,
            payload_bytes=actual_bytes,
            transaction_type=transaction_type,
            criticality=criticality,
            body=body,
        )

    def generate_batch(
        self, n: int, payload_class: PayloadClass, transaction_type: TransactionType = TransactionType.SHARE
    ) -> list[EHRTransaction]:
        return [self.generate(payload_class, transaction_type) for _ in range(n)]
