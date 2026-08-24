from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class QKDResult:
    """Structured result of a QKD key generation simulation."""
    protocol: str
    number_of_bits: int
    sifted_key_length: int
    qber: float
    final_key_length: int
    channel_error_rate: float
    random_seed: Optional[int]
    key_material: Optional[bytes] = field(default=None, repr=False)


class QKDProtocol(ABC):
    """Abstract interface for a Quantum Key Distribution (QKD) protocol."""

    @abstractmethod
    def generate_key(
        self,
        number_of_bits: int,
        channel_error_rate: float,
        random_seed: Optional[int] = None
    ) -> QKDResult:
        """
        Generate a quantum key using the specified protocol.

        Args:
            number_of_bits (int): Total number of random bits/pulses to simulate.
            channel_error_rate (float): The probability of an error on the channel.
            random_seed (Optional[int]): Seed for deterministic behavior.

        Returns:
            QKDResult: A structured object containing the simulation results.
        """
        pass
