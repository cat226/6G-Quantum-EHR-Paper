"""
Per-cell aggregation (Task 6 Section 14, Task 7 Part 8, Task 8 Phase
13). Reads raw JSON-lines transaction events and computes summary
statistics -- mean, median, 95th percentile, and bootstrap confidence
intervals, per Task 7 Part 8's justification (latency is expected to be
right-skewed because of the adaptive controller's bounded-wait
behavior, so a normal-distribution CI would misstate the interval).
"""

from __future__ import annotations

import json
import random
import statistics
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CellSummary:
    experiment_id: str
    baseline: str
    qkd_availability_config: float
    device_count: int
    payload_class: str
    network_load: str
    n_transactions: int
    n_success: int
    successful_transmission_rate: float
    key_establishment_ms_mean: float
    key_establishment_ms_median: float
    key_establishment_ms_p95: float
    key_establishment_ms_ci95_low: float
    key_establishment_ms_ci95_high: float
    payload_encryption_ms_mean: float
    end_to_end_ms_mean: float
    end_to_end_ms_median: float
    end_to_end_ms_p95: float
    communication_overhead_bytes_mean: float
    fallback_frequency: float  # fraction of B5 sessions that used PQC_ONLY


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return float("nan")
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (pct / 100)
    f, c = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def _bootstrap_ci(values: list[float], n_resamples: int = 1000, seed: int = 0) -> tuple[float, float]:
    """95% CI via bootstrap resampling of the mean -- no normality
    assumption (Task 7 Part 8's justification)."""
    if len(values) < 2:
        v = values[0] if values else float("nan")
        return v, v
    rng = random.Random(seed)
    means = []
    n = len(values)
    for _ in range(n_resamples):
        resample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(statistics.mean(resample))
    means.sort()
    lo_idx = int(0.025 * n_resamples)
    hi_idx = int(0.975 * n_resamples)
    return means[lo_idx], means[min(hi_idx, n_resamples - 1)]


def load_events(raw_path: Path) -> list[dict]:
    events = []
    with open(raw_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def summarize_cell(events: list[dict]) -> CellSummary:
    if not events:
        raise ValueError("cannot summarize an empty event list")

    first = events[0]
    n = len(events)
    successes = [e for e in events if e["success"]]
    n_success = len(successes)

    ke_times = [e["key_establishment_ms"] for e in successes]
    e2e_times = [e["end_to_end_ms"] for e in successes]
    overhead = [e["communication_overhead_bytes"] for e in successes]
    # Present on every event written by src/simulation/simulator.py since
    # the M3 fix (Task 8.5); .get() with a 0.0 default keeps this function
    # working against older raw files that predate the field.
    enc_times = [e.get("payload_encryption_ms", 0.0) for e in successes]

    ke_ci_low, ke_ci_high = _bootstrap_ci(ke_times) if ke_times else (float("nan"), float("nan"))

    fallback_events = [
        e for e in events
        if e["baseline"] == "B5" and e.get("mode_used") == "KeySource.PQC_ONLY"
    ]
    b5_events = [e for e in events if e["baseline"] == "B5"]
    fallback_frequency = (
        len(fallback_events) / len(b5_events) if b5_events else float("nan")
    )

    return CellSummary(
        experiment_id=first["experiment_id"],
        baseline=first["baseline"],
        qkd_availability_config=first["qkd_availability_config"],
        device_count=first["device_count"],
        payload_class=first["payload_class"],
        network_load=first["network_load"],
        n_transactions=n,
        n_success=n_success,
        successful_transmission_rate=n_success / n if n else float("nan"),
        key_establishment_ms_mean=statistics.mean(ke_times) if ke_times else float("nan"),
        key_establishment_ms_median=statistics.median(ke_times) if ke_times else float("nan"),
        key_establishment_ms_p95=_percentile(ke_times, 95),
        key_establishment_ms_ci95_low=ke_ci_low,
        key_establishment_ms_ci95_high=ke_ci_high,
        payload_encryption_ms_mean=statistics.mean(enc_times) if enc_times else float("nan"),
        end_to_end_ms_mean=statistics.mean(e2e_times) if e2e_times else float("nan"),
        end_to_end_ms_median=statistics.median(e2e_times) if e2e_times else float("nan"),
        end_to_end_ms_p95=_percentile(e2e_times, 95),
        communication_overhead_bytes_mean=statistics.mean(overhead) if overhead else float("nan"),
        fallback_frequency=fallback_frequency,
    )
