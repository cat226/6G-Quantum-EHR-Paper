from dataclasses import dataclass

@dataclass
class Scenario:
    """
    Defines the configuration parameters for a single simulation run.
    """
    seed: int
    baseline: str
    qkd_availability: int
    device_count: int
    payload_class: str
    network_load: str
    experiment_id: str
    repetitions: int = 1
