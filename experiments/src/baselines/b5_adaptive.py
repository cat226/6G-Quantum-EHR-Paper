import random
from typing import Any
from experiments.src.baselines.baseline_interface import BaselineProtocol, BaselineResult
from experiments.src.baselines.b2_pqc_only import B2PQCOnly
from experiments.src.baselines.b4_static_hybrid import B4StaticHybrid
from experiments.src.adaptive.controller import AdaptiveController
from experiments.src.adaptive.mode_sync import ModeSynchronizer

class B5Adaptive(BaselineProtocol):
    """
    B5: Adaptive Hybrid baseline.
    Switches between PQC_ONLY and HYBRID based on QKD availability.
    """
    def __init__(self):
        self.mode = "ADAPTIVE"
        self.b2 = B2PQCOnly()
        self.b4 = B4StaticHybrid()
        self.mode_sync = ModeSynchronizer()
        
    def initialize(self, seed: int, **kwargs):
        self.rng = random.Random(seed)
        self.b2.initialize(seed)
        self.b4.initialize(seed)
        
    def execute_transaction(self, payload: bytes, qkd_pool: Any = None) -> BaselineResult:
        controller = AdaptiveController(qkd_pool=qkd_pool)
        selected_mode = controller.determine_mode()
        
        # Simulate mode synchronization
        sync_time_ms = self.mode_sync.sync_mode(selected_mode)
        
        if selected_mode == "PQC_ONLY":
            result = self.b2.execute_transaction(payload, qkd_pool)
        else:
            result = self.b4.execute_transaction(payload, qkd_pool)
            
        result.selected_mode = selected_mode
        result.key_establishment_latency_ms += sync_time_ms
        result.total_crypto_latency_ms += sync_time_ms
        
        return result
