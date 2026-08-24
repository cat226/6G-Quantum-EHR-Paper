import argparse
import sys
from experiments.src.runner.experiment_runner import ExperimentRunner

def main():
    parser = argparse.ArgumentParser(description="6G-Quantum-EHR-Paper Simulation Runner")
    parser.add_argument("--config", type=str, required=True, help="Path to pilot configuration YAML")
    parser.add_argument("--raw-dir", type=str, default="experiments/results/pilot/raw", help="Output directory for raw JSONL")
    parser.add_argument("--agg-dir", type=str, default="experiments/results/pilot/aggregated", help="Output directory for aggregated CSV")
    
    args = parser.parse_args()
    
    try:
        runner = ExperimentRunner(args.config, args.raw_dir, args.agg_dir)
        runner.run_pilot()
    except Exception as e:
        print(f"Simulation failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
