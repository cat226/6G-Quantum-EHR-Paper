"""
Re-exports TransactionEvent for the file layout requested in Task 8
Phase 2. The dataclass itself lives in src/metrics/collector.py, next to
MetricsCollector, since the two are tightly coupled (the collector's
record() method is typed directly against this dataclass) -- splitting
them across files would only add an import hop with no benefit. See
docs/implementation_notes.md's "Structural deviations from Task 8 Phase
2" note.
"""

from ..metrics.collector import TransactionEvent  # noqa: F401
