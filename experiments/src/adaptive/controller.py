from experiments.src.qkd_model.qkd_pool import QKDPool

class AdaptiveController:
    """
    Implements the B5 decision policy.
    """
    def __init__(self, qkd_pool: QKDPool, threshold_bits: int = 256):
        self.qkd_pool = qkd_pool
        self.threshold_bits = threshold_bits
        
    def determine_mode(self) -> str:
        """
        Determines the current operating mode based on QKD availability.
        """
        if self.qkd_pool.outage or self.qkd_pool.level < self.threshold_bits:
            return "PQC_ONLY"
        return "HYBRID"
