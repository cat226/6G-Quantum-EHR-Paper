import pytest

from src.qkd.base import QKDProtocol, QKDResult
from src.qkd.bb84 import BB84Protocol

def test_bb84_instantiation():
    """Verify BB84 object can be instantiated and implements interface."""
    protocol = BB84Protocol()
    assert isinstance(protocol, QKDProtocol)

def test_basic_key_generation():
    """Verify basic key generation succeeds and returns correct type."""
    protocol = BB84Protocol()
    result = protocol.generate_key(100, 0.0)
    assert isinstance(result, QKDResult)
    assert result.protocol == "BB84"
    assert result.number_of_bits == 100
    assert result.channel_error_rate == 0.0

def test_result_object_fields():
    """Verify the result object has all required fields."""
    protocol = BB84Protocol()
    result = protocol.generate_key(100, 0.0, random_seed=42)
    assert hasattr(result, 'protocol')
    assert hasattr(result, 'number_of_bits')
    assert hasattr(result, 'sifted_key_length')
    assert hasattr(result, 'qber')
    assert hasattr(result, 'final_key_length')
    assert hasattr(result, 'channel_error_rate')
    assert hasattr(result, 'random_seed')
    assert result.random_seed == 42

def test_identical_seed_identical_results():
    """Verify that using the same seed produces identical results."""
    protocol = BB84Protocol()
    res1 = protocol.generate_key(1000, 0.05, random_seed=42)
    res2 = protocol.generate_key(1000, 0.05, random_seed=42)
    assert res1 == res2

def test_different_seeds_different_results():
    """Verify that different seeds produce different simulation outcomes."""
    protocol = BB84Protocol()
    res1 = protocol.generate_key(10000, 0.05, random_seed=42)
    res2 = protocol.generate_key(10000, 0.05, random_seed=43)
    assert res1 != res2

def test_zero_channel_error_produces_zero_qber():
    """Verify zero channel error produces QBER = 0 for deterministic setup."""
    protocol = BB84Protocol()
    result = protocol.generate_key(1000, 0.0, random_seed=1)
    assert result.qber == 0.0

def test_qber_is_within_bounds():
    """Verify QBER is within [0, 1]."""
    protocol = BB84Protocol()
    result = protocol.generate_key(1000, 0.5, random_seed=123)
    assert 0.0 <= result.qber <= 1.0

def test_sifted_key_length_bounds():
    """Verify sifted key length is never greater than number_of_bits."""
    protocol = BB84Protocol()
    result = protocol.generate_key(1000, 0.1, random_seed=99)
    assert 0 <= result.sifted_key_length <= result.number_of_bits

def test_final_key_length_bounds():
    """Verify final key length is never greater than sifted_key_length."""
    protocol = BB84Protocol()
    result = protocol.generate_key(1000, 0.1, random_seed=99)
    assert 0 <= result.final_key_length <= result.sifted_key_length

def test_zero_bit_input():
    """Verify zero-bit input is handled correctly (zero QBER/length)."""
    protocol = BB84Protocol()
    result = protocol.generate_key(0, 0.1, random_seed=42)
    assert result.number_of_bits == 0
    assert result.sifted_key_length == 0
    assert result.qber == 0.0
    assert result.final_key_length == 0

def test_invalid_bits_input():
    """Verify invalid bit input is rejected."""
    protocol = BB84Protocol()
    with pytest.raises(ValueError, match="number_of_bits must be non-negative"):
        protocol.generate_key(-1, 0.0)

def test_invalid_channel_error_rate():
    """Verify invalid channel error rate is rejected."""
    protocol = BB84Protocol()
    with pytest.raises(ValueError, match="channel_error_rate must be between 0.0 and 1.0"):
        protocol.generate_key(100, -0.1)
    with pytest.raises(ValueError, match="channel_error_rate must be between 0.0 and 1.0"):
        protocol.generate_key(100, 1.1)

class DummyProtocol(QKDProtocol):
    """A dummy protocol to test the abstraction layer."""
    def generate_key(
        self,
        number_of_bits: int,
        channel_error_rate: float,
        random_seed: int | None = None
    ) -> QKDResult:
        return QKDResult(
            protocol="Dummy",
            number_of_bits=number_of_bits,
            sifted_key_length=number_of_bits,
            qber=channel_error_rate,
            final_key_length=number_of_bits,
            channel_error_rate=channel_error_rate,
            random_seed=random_seed
        )

def test_protocol_abstraction():
    """Verify protocol abstraction can support another future implementation."""
    protocol = DummyProtocol()
    result = protocol.generate_key(10, 0.5)
    assert result.protocol == "Dummy"
    assert result.number_of_bits == 10
    assert result.qber == 0.5
