#!/usr/bin/env python3
"""
Pilot experiment runner (Task 7 Part 7, Task 8 Phase 14/15).

Usage:
    python experiments/run_pilot.py --config config/pilot.yaml --seed 42 --output results/raw/

Supports --config, --seed, --output per Task 8 Phase 15's explicit
requirement. Every run's configuration, seed, software version, and
timestamp are saved alongside the raw measurements.

By default this runs the SINGLE-CELL smoke path unless --full-pilot is
passed -- per Task 8 Phase 18's explicit instruction not to run the
full experiment yet. Running all 30 pilot configurations x repetitions
is a deliberate, separate action (--full-pilot), not the default.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.adaptive.controller import AdaptiveController, AdaptiveThresholds
from src.baselines.baselines import BaselineID
from src.simulation.simulator import CellConfig, run_cell
from src.utils.config import load_config
from src.utils.logging import get_logger
from src.utils.random import SeedManager
from src.workload.ehr_generator import PayloadClass

logger = get_logger("run_pilot")


def _record_environment(output_dir: Path, config_path: str, seed: int) -> None:
    """Task 8 Phase 15: save configuration, seed, software version, and
    timestamp with each experiment."""
    env_info = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "seed": seed,
        "python_version": sys.version,
        "platform": platform.platform(),
    }
    try:
        import oqs

        env_info["liboqs_python_version"] = getattr(oqs, "__version__", "unknown")
    except Exception:
        env_info["liboqs_python_version"] = "not available"

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "environment.json", "w") as fh:
        json.dump(env_info, fh, indent=2)


def run_single_cell(config: dict, output_dir: Path, seed: int, cell_overrides: dict | None = None) -> str:
    """Runs exactly ONE pilot configuration -- the "exact command for
    running ONE pilot configuration" Task 8 asks the final report to
    include is built around this function."""
    overrides = cell_overrides or {}
    baseline_id = BaselineID(overrides.get("baseline", config["baselines"][0]))
    qkd_availability = overrides.get("qkd_availability", config["qkd_availability_levels"][0])
    device_count = overrides.get("device_count", config["device_counts"][0])
    payload_class = PayloadClass(overrides.get("payload_class", config["payload_classes"][0]))
    network_load = overrides.get("network_load", config["network_loads"][0])

    thresholds = AdaptiveThresholds(**config["adaptive_thresholds"])

    def controller_factory():
        return AdaptiveController(thresholds)

    experiment_id = (
        f"baseline={baseline_id.value}_qkd={int(qkd_availability*100)}"
        f"_devices={device_count}_payload={payload_class.value}"
        f"_load={network_load}_seed={seed}"
    )

    cell_config = CellConfig(
        experiment_id=experiment_id,
        baseline_id=baseline_id,
        qkd_availability_config=qkd_availability,
        device_count=device_count,
        payload_class=payload_class,
        network_load=network_load,
        seed=seed,
        n_transactions_per_device=config["n_transactions_per_device"],
        sim_duration_seconds=config["sim_duration_seconds"],
    )

    logger.info(f"running cell: {experiment_id}")
    path = run_cell(cell_config, str(output_dir), controller_factory)
    logger.info(f"wrote raw events to: {path}")
    return path


def run_full_pilot(config: dict, output_dir: Path, base_seed: int) -> list[str]:
    """Runs all 30 pilot configurations x repetitions_per_cell. NOT run
    by default (Task 8 Phase 18) -- only invoked with --full-pilot."""
    seed_mgr = SeedManager(base_seed)
    paths = []
    n_cells = 0
    for baseline in config["baselines"]:
        for qkd_avail in config["qkd_availability_levels"]:
            for device_count in config["device_counts"]:
                for payload_class in config["payload_classes"]:
                    for network_load in config["network_loads"]:
                        n_cells += 1
                        for rep in range(config["repetitions_per_cell"]):
                            seed_name = f"{baseline}-{qkd_avail}-{device_count}-{payload_class}-{network_load}-rep{rep}"
                            seed = seed_mgr.sub_seed(seed_name)
                            overrides = {
                                "baseline": baseline,
                                "qkd_availability": qkd_avail,
                                "device_count": device_count,
                                "payload_class": payload_class,
                                "network_load": network_load,
                            }
                            path = run_single_cell(config, output_dir, seed, overrides)
                            paths.append(path)
    logger.info(f"full pilot complete: {n_cells} cells, {len(paths)} total runs")
    return paths


def main():
    parser = argparse.ArgumentParser(description="Run the QKD-PQC EHR simulation pilot")
    parser.add_argument("--config", required=True, help="path to pilot.yaml")
    parser.add_argument("--seed", type=int, required=True, help="base random seed")
    parser.add_argument("--output", required=True, help="output directory for raw results")
    parser.add_argument(
        "--full-pilot",
        action="store_true",
        help="run all 30 configurations x repetitions (NOT the default -- Task 8 Phase 18)",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="single-cell mode: which baseline (B1-B5); default: first in config",
    )
    parser.add_argument("--qkd-availability", type=float, default=None)
    parser.add_argument("--device-count", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = Path(args.output)
    _record_environment(output_dir, args.config, args.seed)

    if args.full_pilot:
        run_full_pilot(config, output_dir, args.seed)
    else:
        overrides = {}
        if args.baseline:
            overrides["baseline"] = args.baseline
        if args.qkd_availability is not None:
            overrides["qkd_availability"] = args.qkd_availability
        if args.device_count is not None:
            overrides["device_count"] = args.device_count
        run_single_cell(config, output_dir, args.seed, overrides)


if __name__ == "__main__":
    main()
