from experiments.src.baselines import get_baseline
from experiments.src.qkd_model.qkd_pool import QKDPool
from experiments.src.qkd_model.qkd_availability import QKDAvailabilityModel
from experiments.src.workload.ehr_generator import EHRGenerator
from experiments.src.network.sixg_model import SixGModel
from experiments.src.simulation.scenario import Scenario

class SimulationEngine:
    """
    Deterministic discrete-event simulation engine for the EHR experiments.
    """
    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        
        if self.scenario.seed is None:
            raise ValueError("Explicit seed is required for reproducibility.")
            
        # 1. Initialize workload
        self.workload = EHRGenerator(seed=self.scenario.seed)
        
        # 2. Initialize QKD Model (Modeled: 1 Mbps capacity, 256k generation rate per tick)
        self.qkd_pool = QKDPool(capacity=1024*1024, generation_rate=256*1024)
        self.qkd_availability = QKDAvailabilityModel(
            target_availability=self.scenario.qkd_availability,
            pool=self.qkd_pool,
            seed=self.scenario.seed
        )
        
        # 3. Initialize Network
        self.network = SixGModel(load=self.scenario.network_load)
        
        # 4. Initialize Baseline
        self.baseline_impl = get_baseline(self.scenario.baseline)
        self.baseline_impl.initialize(seed=self.scenario.seed)

    def run_transaction(self):
        """
        Executes a single transaction within the scenario.
        Returns a dict of metrics.
        """
        # Start of simulated continuous timeline for this transaction
        t_ms = 0.0
        
        # Generate workload
        txn = self.workload.generate_transaction(size_class=self.scenario.payload_class)
        
        # Payload processing delay simulation based on deterministic RNG
        processing_delay = self.workload.rng.uniform(1.0, 5.0)
        t_ms += processing_delay
        
        # Initial routing network delay
        nw_latency = self.network.get_network_latency_ms(len(txn["payload"]))
        edge_delay = self.network.get_edge_processing_delay_ms()
        t_ms += nw_latency + edge_delay
        
        # Advance simulation time for models to timestamp t_ms
        self.qkd_availability.update(t_ms)
        
        # Execute baseline at time t_ms
        result = self.baseline_impl.execute_transaction(txn["payload"], self.qkd_pool)
        
        # Add post-crypto transmission latency
        total_latency = t_ms + result.total_crypto_latency_ms
        
        # Return structured metrics record (No secrets)
        return {
            "experiment_id": self.scenario.experiment_id,
            "baseline": self.scenario.baseline,
            "seed": self.scenario.seed,
            "qkd_availability": self.scenario.qkd_availability,
            "device_count": self.scenario.device_count,
            "payload_class": self.scenario.payload_class,
            "network_load": self.scenario.network_load,
            "transaction_id": txn["transaction_id"],
            "transaction_type": txn["type"],
            "criticality": txn["criticality"],
            "selected_mode": result.selected_mode,
            "success": result.success,
            "failure_reason": result.failure_reason,
            "latency_ms": total_latency if result.success else 0.0,
            "key_establishment_latency_ms": result.key_establishment_latency_ms,
            "authentication_latency_ms": result.authentication_latency_ms,
            "encryption_latency_ms": result.encryption_latency_ms,
            "network_latency_ms": nw_latency,
            "payload_bytes": len(txn["payload"]),
            "qkd_pool_state": self.qkd_pool.available_fraction()
        }
