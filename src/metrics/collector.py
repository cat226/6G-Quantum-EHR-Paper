"""
Metrics collection (Task 6 Section 14, Task 8 Phase 13).

Records raw, per-transaction events first -- metrics are computed from
raw data, never the reverse (Task 8 Phase 13's explicit instruction:
"Do not calculate metrics from aggregated values if raw event data is
available. Save raw measurements first.").

Every record carries the full experiment-identifying context (timestamp,
experiment ID, baseline, QKD availability, device count, payload class,
network load, random seed) per Task 8 Phase 13, so raw logs are
self-describing and don't depend on filename parsing to be analyzed
correctly.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class TransactionEvent:
    """One row = one transaction. This is the raw unit of record; all
    Task 6 Section 14 metrics are derivable from a collection of these
    without needing any other data source."""

    timestamp: float
    experiment_id: str
    baseline: str
    qkd_availability_config: float  # the *configured* nominal availability for this cell
    device_count: int
    payload_class: str
    network_load: str
    seed: int

    transaction_id: str
    success: bool
    key_establishment_ms: float
    #: AES-256-GCM encrypt+decrypt round-trip cost for the EHR payload
    #: itself (0.0 on a failed transaction, where no payload is ever
    #: encrypted). Distinct from key_establishment_ms, which covers only
    #: deriving the session key -- this is the cost of actually using it.
    payload_encryption_ms: float
    network_latency_ms: float
    end_to_end_ms: float
    communication_overhead_bytes: int
    payload_bytes: int
    mode_used: str | None  # KeySource value, or None on failure before a mode was chosen
    controller_state: str | None
    failure_reason: str | None


class MetricsCollector:
    """Writes TransactionEvent records to a JSON-lines file as they happen
    (Task 8 Phase 13/Task 6 Section 18: no need to hold the whole run in
    memory, directly loadable via pandas.read_json(lines=True)).

    The output file is truncated when a collector opens it, then written
    incrementally for the lifetime of that collector -- one open() call
    covers one entire run's worth of record() calls, so nothing within a
    run is lost. What truncation prevents is a SEPARATE run (e.g. a retry
    after a crash, or a rerun with tweaked parameters) silently appending
    its transactions onto a previous run's file: two runs sharing an
    experiment_id and output path would otherwise double-count that
    cell's transactions with no error and no warning (Task 8.5 finding
    F6). A rerun now overwrites cleanly instead.
    """

    def __init__(self, output_path: Path):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.output_path, "w", encoding="utf-8")
        self._count = 0

    def record(self, event: TransactionEvent) -> None:
        self._fh.write(json.dumps(asdict(event)) + "\n")
        self._fh.flush()
        self._count += 1

    @property
    def count(self) -> int:
        return self._count

    def close(self) -> None:
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
