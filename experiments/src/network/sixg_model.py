class SixGModel:
    """
    Simplified 6G-edge abstraction. NOT a finalized protocol stack.
    """
    def __init__(self, load: str = "nominal"):
        self.load = load
        
    def get_network_latency_ms(self, payload_size_bytes: int) -> float:
        """
        Calculates a simplified network transmission latency.
        """
        # Nominal baseline: ~1ms fixed access latency + propagation delay
        base_latency = 1.0 
        
        # Assume a simple throughput (e.g., 10 Gbps = ~1.25 GB/s)
        throughput_bytes_per_ms = 1_250_000
        
        transmission_delay = payload_size_bytes / throughput_bytes_per_ms
        
        return base_latency + transmission_delay
        
    def get_edge_processing_delay_ms(self) -> float:
        """
        Calculates a simplified edge processing delay.
        """
        return 0.5
