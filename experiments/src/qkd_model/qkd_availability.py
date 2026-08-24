import random
from typing import Optional
from .qkd_pool import QKDPool

class QKDAvailabilityModel:
    """
    Models QKD availability scenarios deterministically (100%, 50%, 0%).
    """
    def __init__(self, target_availability: int, pool: QKDPool, seed: int):
        if target_availability not in [100, 50, 0]:
            raise ValueError(f"Unsupported availability level: {target_availability}")
            
        self.target_availability = target_availability
        self.pool = pool
        self.rng = random.Random(seed)
        self.tick_count = 0
        
        # Immediately apply 0% constraint
        if self.target_availability == 0:
            self.pool.set_outage(True)
            self.pool.level = 0
        elif self.target_availability == 100:
            self.pool.set_outage(False)

    def update(self, time_ms: float):
        """
        Advances the simulation time for the QKD model to the specified time_ms.
        Replenishes the pool and determines availability state based on time.
        """
        if self.target_availability == 100:
            self.pool.set_outage(False)
            self.pool.update()
        elif self.target_availability == 0:
            self.pool.set_outage(True)
        elif self.target_availability == 50:
            # We will use the RNG state initialized by seed to derive a deterministic
            # phase offset for this specific repetition/cell.
            # But wait, rng.random() is stateful. We shouldn't call it on every update,
            # otherwise it consumes RNG state unpredictably based on how many times update() is called.
            # We'll calculate it once during initialization.
            if not hasattr(self, 'phase_offset_ms'):
                self.phase_offset_ms = self.rng.uniform(0, 10.0) # 0 to 10ms phase offset
            
            # Simple alternating outage model: 5ms ON, 5ms OFF (period = 10ms)
            # 50% availability
            cycle_time = (time_ms + self.phase_offset_ms) % 10.0
            if cycle_time < 5.0: # Available
                self.pool.set_outage(False)
                self.pool.update()
            else: # Outage
                self.pool.set_outage(True)
