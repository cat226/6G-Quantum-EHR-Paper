import random
from typing import Dict, Any, List

class EHRGenerator:
    """
    Synthetic EHR transaction generator.
    Never uses real patient data.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.transaction_counter = 0
        
        # Payload size classes (MODELED ASSUMPTIONS)
        self.PAYLOAD_SIZES = {
            "SMALL": (1024, 5120),          # 1-5 KB
            "MEDIUM": (20480, 81920),       # 20-80 KB
            "LARGE": (204800, 1048576)      # 200 KB - 1 MB
        }
        
        self.TRANSACTION_TYPES = ["READ", "WRITE", "SHARE"]
        self.CRITICALITY = ["ROUTINE", "EMERGENCY"]
        
    def generate_payload(self, size_class: str) -> bytes:
        """
        Generates a synthetic payload of random bytes.
        No plaintext EHR data is used.
        """
        if size_class not in self.PAYLOAD_SIZES:
            raise ValueError(f"Unknown payload size class: {size_class}")
            
        min_size, max_size = self.PAYLOAD_SIZES[size_class]
        actual_size = self.rng.randint(min_size, max_size)
        
        # We don't actually need to allocate massive random byte arrays and slow down the sim.
        # We can just allocate a zeroed array of the correct size to simulate network bytes,
        # but to satisfy AEAD encryption we should use bytes.
        return bytes(actual_size)
        
    def generate_transaction(self, size_class: str = "MEDIUM", device_id: str = "dev-0") -> Dict[str, Any]:
        """
        Generates metadata and synthetic payload for a transaction.
        """
        self.transaction_counter += 1
        
        # In this research, SHARE is the primary emphasis, but we can randomly select.
        # However, the pilot only tests MEDIUM payloads.
        t_type = self.rng.choices(self.TRANSACTION_TYPES, weights=[0.2, 0.2, 0.6])[0]
        criticality = self.rng.choice(self.CRITICALITY)
        
        payload_bytes = self.generate_payload(size_class)
        
        return {
            "transaction_id": f"txn-{self.transaction_counter}",
            "device_id": device_id,
            "type": t_type,
            "criticality": criticality,
            "payload_class": size_class,
            "payload": payload_bytes
        }
