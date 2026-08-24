from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import mlkem

from src.pqc.base import PQCProtocol, PQCResult


class MLKEMProtocol(PQCProtocol):
    """
    ML-KEM adapter wrapping the cryptography library implementation.
    This serves as the project's baseline configuration.
    """

    def __init__(self, parameter_set: str = "ML-KEM-768"):
        """
        Initialize the ML-KEM protocol with a specific parameter set.

        Args:
            parameter_set: The exact supported parameter set identifier.
        """
        self.algorithm = "ML-KEM"
        self.parameter_set = parameter_set

        if parameter_set == "ML-KEM-768":
            self._key_class = mlkem.MLKEM768PrivateKey
            self._pub_class = mlkem.MLKEM768PublicKey
            self.public_key_length = 1184
            self.secret_key_length = 64
            self.ciphertext_length = 1088
            self.shared_secret_length = 32
        elif parameter_set == "ML-KEM-1024":
            self._key_class = mlkem.MLKEM1024PrivateKey
            self._pub_class = mlkem.MLKEM1024PublicKey
            self.public_key_length = 1568
            self.secret_key_length = 64
            self.ciphertext_length = 1568
            self.shared_secret_length = 32
        else:
            raise ValueError(f"Unsupported ML-KEM parameter set: {parameter_set}")

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generates a new public and secret key pair using cryptographically secure randomness."""
        priv_key = self._key_class.generate()
        pub_key = priv_key.public_key()

        # Serialize to bytes representing the key material
        pub_bytes = pub_key.public_bytes_raw()
        priv_bytes = priv_key.private_bytes_raw()

        return pub_bytes, priv_bytes

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes, PQCResult]:
        """Encapsulates a shared secret for the given public key."""
        try:
            pub = self._pub_class.from_public_bytes(public_key)
        except ValueError as e:
            raise ValueError("Malformed public key") from e

        encap_result = pub.encapsulate()
        # cryptography >= 50.0.0 returns (shared_secret, ciphertext) for ML-KEM
        shared_secret, ciphertext = encap_result

        result = PQCResult(
            algorithm=self.algorithm,
            parameter_set=self.parameter_set,
            ciphertext_length=len(ciphertext),
            shared_secret_length=len(shared_secret),
            public_key_length=self.public_key_length,
            secret_key_length=self.secret_key_length
        )

        return ciphertext, shared_secret, result

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """Decapsulates the shared secret from the ciphertext using the secret key."""
        if len(secret_key) != self.secret_key_length:
            raise ValueError("Malformed secret key")

        try:
            priv = self._key_class.from_seed_bytes(secret_key)
        except ValueError as e:
            raise ValueError("Malformed secret key") from e

        try:
            shared_secret = priv.decapsulate(ciphertext)
        except ValueError as e:
            # Re-raise with our own explicit message for consistency
            raise ValueError("Invalid ciphertext or decapsulation failed") from e

        return shared_secret
