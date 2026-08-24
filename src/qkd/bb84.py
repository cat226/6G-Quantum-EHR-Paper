import random
from typing import Optional

from .base import QKDProtocol, QKDResult


class BB84Protocol(QKDProtocol):
    """
    Simplified software model of the BB84 QKD protocol.

    This is NOT a physically accurate quantum simulator. It models
    the protocol logic probabilistically using pseudo-random numbers
    to support deterministic testing and high-level evaluation.
    """

    def generate_key(
        self,
        number_of_bits: int,
        channel_error_rate: float,
        random_seed: Optional[int] = None
    ) -> QKDResult:
        if number_of_bits < 0:
            raise ValueError("number_of_bits must be non-negative")
        if not (0.0 <= channel_error_rate <= 1.0):
            raise ValueError("channel_error_rate must be between 0.0 and 1.0")

        rng = random.Random(random_seed)

        # Sifting process
        # For each bit, Alice and Bob each choose a random basis (0 or 1)
        # If their bases match, they keep the bit (this is the sifted key).
        sifted_bits = []
        for _ in range(number_of_bits):
            alice_bit = rng.randint(0, 1)
            alice_basis = rng.randint(0, 1)
            bob_basis = rng.randint(0, 1)

            if alice_basis == bob_basis:
                sifted_bits.append(alice_bit)

        sifted_key_length = len(sifted_bits)

        # Simplified Channel Error Model
        # Errors are applied probabilistically to the sifted key.
        errors = 0
        final_key = []
        for bit in sifted_bits:
            if rng.random() < channel_error_rate:
                errors += 1
                final_key.append(1 - bit) # flip bit
            else:
                final_key.append(bit)

        # Calculate QBER
        if sifted_key_length > 0:
            qber = errors / sifted_key_length
        else:
            qber = 0.0

        # Final key length (no privacy amplification in this task)
        final_key_length = len(final_key)

        # Pack bits into bytes for cryptographic consumption
        packed_key = bytearray()
        for i in range(0, final_key_length, 8):
            byte_val = 0
            for j, bit in enumerate(final_key[i:i+8]):
                byte_val |= (bit << (7 - j))
            packed_key.append(byte_val)

        return QKDResult(
            protocol="BB84",
            number_of_bits=number_of_bits,
            sifted_key_length=sifted_key_length,
            qber=qber,
            final_key_length=final_key_length,
            channel_error_rate=channel_error_rate,
            random_seed=random_seed,
            key_material=bytes(packed_key)
        )
