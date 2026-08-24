from typing import Optional

class QKDPool:
    """
    Deterministic simulation model for QKD key availability.
    """
    def __init__(
        self, 
        capacity: int, 
        generation_rate: int, 
        initial_level: Optional[int] = None
    ):
        self.capacity = capacity
        self.generation_rate = generation_rate
        self.level = initial_level if initial_level is not None else capacity
        self.outage = False

    def debit(self, n_bits: int) -> bool:
        """
        Attempt to consume n_bits from the pool.
        Returns True if successful, False if insufficient material.
        """
        if self.outage:
            return False
            
        if self.level >= n_bits:
            self.level -= n_bits
            return True
        return False

    def available_fraction(self) -> float:
        """Returns the fraction of the pool currently filled."""
        if self.capacity == 0:
            return 0.0
        return self.level / self.capacity

    def update(self):
        """Replenish the pool based on the generation rate."""
        if not self.outage:
            self.level = min(self.capacity, self.level + self.generation_rate)
            
    def set_outage(self, status: bool):
        """Forces an outage state where consumption is blocked."""
        self.outage = status
