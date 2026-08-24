import os
import uuid
import yaml
from experiments.src.simulation.scenario import Scenario
from experiments.src.simulation.engine import SimulationEngine
from experiments.src.metrics.collector import MetricsCollector
from experiments.src.metrics.aggregator import MetricsAggregator

class ExperimentRunner:
    """
    Executes the configured experiment pilot and ensures deterministic fairness.
    """
    def __init__(self, config_file: str, raw_dir: str, agg_dir: str):
        self.config_file = config_file
        self.raw_dir = raw_dir
        self.agg_dir = agg_dir
        
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.base_seed = self.config.get("base_seed")
        if self.base_seed is None:
            raise ValueError("Configuration MUST provide a base_seed for reproducibility.")
            
    def run_pilot(self):
        """
        Executes the 30-cell pilot configuration (150 scenarios total).
        """
        experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
        collector = MetricsCollector(os.path.join(self.raw_dir, f"{experiment_id}.jsonl"))
        
        baselines = self.config["pilot"]["baselines"]
        availabilities = self.config["pilot"]["qkd_availability"]
        devices = self.config["pilot"]["devices"]
        payload = self.config["pilot"]["payload"]
        network = self.config["pilot"]["network"]
        repetitions = self.config["pilot"]["repetitions"]
        
        expected_cells = len(baselines) * len(availabilities) * len(devices)
        if expected_cells != 30:
            raise ValueError(f"Pilot configuration must produce exactly 30 cells. Found {expected_cells}.")
            
        # Fairness Audit structure
        # Key: (availability, device, repetition), Value: list of generated payload sizes
        fairness_ledger = {}
            
        run_count = 0
        for b in baselines:
            for a in availabilities:
                for d in devices:
                    for r in range(repetitions):
                        # Derive a deterministic sub-seed for this cell repetition
                        # Notice we omit the baseline from the seed derivation to ensure
                        # that all baselines face the exact same random workload/QKD state
                        cell_seed = hash(f"{self.base_seed}_{a}_{d}_{payload}_{network}_{r}")
                        
                        scenario = Scenario(
                            seed=cell_seed,
                            baseline=b,
                            qkd_availability=a,
                            device_count=d,
                            payload_class=payload,
                            network_load=network,
                            experiment_id=experiment_id,
                            repetitions=1
                        )
                        
                        engine = SimulationEngine(scenario)
                        metrics = engine.run_transaction()
                        collector.record(metrics)
                        
                        # Fairness check recording
                        ledger_key = (a, d, r)
                        payload_size = metrics["payload_bytes"]
                        
                        if ledger_key not in fairness_ledger:
                            fairness_ledger[ledger_key] = payload_size
                        else:
                            if fairness_ledger[ledger_key] != payload_size:
                                raise RuntimeError("FAIRNESS AUDIT FAILED: Non-deterministic behavior across baselines detected.")
                                
                        run_count += 1
                        
        print(f"Completed {run_count} executions. Fairness audit passed.")
        
        # Aggregate
        aggregator = MetricsAggregator(self.raw_dir, self.agg_dir)
        aggregator.aggregate()
        print(f"Results aggregated to {self.agg_dir}/aggregated_results.csv")
