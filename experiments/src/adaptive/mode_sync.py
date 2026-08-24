class ModeSynchronizer:
    """
    Abstractions for mode synchronization across the network.
    A mode mismatch must result in a controlled failure rather than silent interpretation.
    """
    def __init__(self, base_network_latency_ms: float = 2.0):
        self.latency = base_network_latency_ms
        
    def sync_mode(self, proposed_mode: str) -> float:
        """
        Simulates the time taken to agree on a mode (1 RTT).
        Returns the elapsed latency in ms.
        """
        # Client proposes mode, Server confirms it
        return self.latency * 2
