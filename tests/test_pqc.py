import pytest
from src.pqc.ml_kem import MLKEMProtocol
from src.pqc.base import PQCProtocol, PQCResult

def test_pqc_instantiation():
    """Test that the ML-KEM adapter can be instantiated."""
    pqc = MLKEMProtocol(parameter_set="ML-KEM-768")
    assert isinstance(pqc, PQCProtocol)
    assert pqc.algorithm == "ML-KEM"
    assert pqc.parameter_set == "ML-KEM-768"

def test_unsupported_parameter_set():
    """Test that unsupported parameter sets raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported ML-KEM parameter set"):
        MLKEMProtocol(parameter_set="ML-KEM-9000")

def test_keypair_generation():
    """Test keypair generation yields correctly sized public and private keys."""
    pqc = MLKEMProtocol()
    pub_key, priv_key = pqc.generate_keypair()

    assert pub_key is not None
    assert priv_key is not None
    assert len(pub_key) == pqc.public_key_length
    assert len(priv_key) == pqc.secret_key_length

def test_encapsulation_decapsulation_success():
    """Test successful encapsulation and decapsulation."""
    pqc = MLKEMProtocol()
    pub_key, priv_key = pqc.generate_keypair()

    ciphertext, shared_secret, metadata = pqc.encapsulate(pub_key)

    assert ciphertext is not None
    assert shared_secret is not None
    assert len(ciphertext) == pqc.ciphertext_length
    assert len(shared_secret) == pqc.shared_secret_length

    # Metadata assertions
    assert isinstance(metadata, PQCResult)
    assert metadata.algorithm == "ML-KEM"
    assert metadata.parameter_set == "ML-KEM-768"
    assert metadata.ciphertext_length == pqc.ciphertext_length
    assert metadata.shared_secret_length == pqc.shared_secret_length

    # Check that secrets don't leak into metadata
    assert not hasattr(metadata, "shared_secret")
    assert not hasattr(metadata, "private_key")

    # Decapsulate
    decapsulated_secret = pqc.decapsulate(ciphertext, priv_key)

    # The expected correctness property
    assert shared_secret == decapsulated_secret

def test_invalid_public_key():
    """Test encapsulation with malformed public key."""
    pqc = MLKEMProtocol()
    bad_pub_key = b"A" * (pqc.public_key_length - 1)

    with pytest.raises(ValueError, match="Malformed public key"):
        pqc.encapsulate(bad_pub_key)

def test_invalid_secret_key():
    """Test decapsulation with malformed secret key."""
    pqc = MLKEMProtocol()
    pub_key, priv_key = pqc.generate_keypair()
    ciphertext, _, _ = pqc.encapsulate(pub_key)

    bad_priv_key = b"B" * (pqc.secret_key_length - 1)

    with pytest.raises(ValueError, match="Malformed secret key"):
        pqc.decapsulate(ciphertext, bad_priv_key)

def test_invalid_ciphertext():
    """Test decapsulation with invalid ciphertext rejects or handles safely."""
    pqc = MLKEMProtocol()
    pub_key, priv_key = pqc.generate_keypair()
    ciphertext, _, _ = pqc.encapsulate(pub_key)

    # Mutate the ciphertext
    mutated_ciphertext = bytearray(ciphertext)
    mutated_ciphertext[0] ^= 0xFF

    # ML-KEM uses implicit rejection, so decapsulating a mutated ciphertext
    # will return a deterministically generated pseudo-random shared secret
    # that does NOT match the original shared secret.
    # cryptography 50.0.0 strictly enforces this.
    wrong_secret = pqc.decapsulate(bytes(mutated_ciphertext), priv_key)

    # Verify the generated secret is 32 bytes
    assert len(wrong_secret) == pqc.shared_secret_length

    # Verify it does not match the original shared secret
    original_secret = pqc.decapsulate(ciphertext, priv_key)
    assert wrong_secret != original_secret

    # Verify that completely invalid sizes raise an exception
    bad_ciphertext_size = b"C" * (pqc.ciphertext_length - 1)
    with pytest.raises(ValueError):
        pqc.decapsulate(bad_ciphertext_size, priv_key)

def test_repeated_operations_independent():
    """Test that repeated operations generate independent cryptographic outputs."""
    pqc = MLKEMProtocol()

    # Keypair generation is randomized
    pub1, priv1 = pqc.generate_keypair()
    pub2, priv2 = pqc.generate_keypair()
    assert pub1 != pub2
    assert priv1 != priv2

    # Encapsulation is randomized
    ct1, ss1, _ = pqc.encapsulate(pub1)
    ct2, ss2, _ = pqc.encapsulate(pub1)
    assert ct1 != ct2
    assert ss1 != ss2
