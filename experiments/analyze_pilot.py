#!/usr/bin/env python3
"""
Pilot results analysis (Task 7 Part 7/8's stated purpose: produce
descriptive per-cell summaries and the variance estimate that will set
the full study's repetition count -- not paper-ready findings).

Groups raw transaction events by cell (baseline, qkd_availability_config,
device_count -- payload_class and network_load are held constant across
the pilot per config/pilot.yaml) and runs each cell's pooled repetitions
through src/metrics/aggregator.summarize_cell(), which already computes
mean/median/p95 and bootstrap 95% CIs (Task 7 Part 8's justification:
latency is expected to be right-skewed by the adaptive controller's
bounded wait, so a normal-distribution CI would misstate the interval).

Deliberately does NOT implement between-baseline hypothesis testing
(Mann-Whitney U, Task 7 Part 8) -- that remains explicitly deferred
(docs/implementation_notes.md Part II Section 6) until a decision is
made on which comparisons the manuscript actually needs. This script
produces descriptive statistics only.

Usage:
    python experiments/analyze_pilot.py \
        --input results/raw/pilot \
        --output results/processed/pilot_summary.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import asdict, fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.metrics.aggregator import load_events, summarize_cell


def group_by_cell(input_dir: Path) -> dict[tuple, list[dict]]:
    """Pools every repetition's raw events into one list per (baseline,
    qkd_availability_config, device_count) cell. Payload class and
    network load are cell-identifying fields too in general, but the
    pilot matrix (config/pilot.yaml) holds them constant, so grouping on
    the three swept dimensions is sufficient here and keeps the grouping
    key readable."""
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for path in sorted(input_dir.glob("*.jsonl")):
        for event in load_events(path):
            key = (
                event["baseline"],
                event["qkd_availability_config"],
                event["device_count"],
            )
            cells[key].append(event)
    return cells


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize pilot raw results per cell")
    parser.add_argument("--input", default="results/raw/pilot", help="directory of raw .jsonl files")
    parser.add_argument("--output", default="results/processed/pilot_summary.csv", help="output CSV path")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_path = Path(args.output)

    cells = group_by_cell(input_dir)
    if not cells:
        print(f"no .jsonl files found under {input_dir}", file=sys.stderr)
        sys.exit(1)

    summaries = [summarize_cell(events) for _, events in sorted(cells.items())]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [f.name for f in fields(summaries[0])]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for s in summaries:
            writer.writerow(asdict(s))

    print(f"{len(summaries)} cells summarized -> {output_path}")
    total_txns = sum(s.n_transactions for s in summaries)
    print(f"{total_txns} total transactions pooled across all repetitions")


if __name__ == "__main__":
    main()
