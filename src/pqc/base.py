import abc
from dataclasses import dataclass
from typing import Tuple

@dataclass
class PQCResult:
    """Structured result model for PQC operations."""
    algorithm: str
    parameter_set: str
    ciphertext_length: int
    shared_secret_length: int
    public_key_length: int
    secret_key_length: int


class PQCProtocol(abc.ABC):
    """
    Abstract base class representing a generic Key Encapsulation Mechanism (KEM).
    """

    @abc.abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generates a public and secret key pair.

        Returns:
            Tuple[bytes, bytes]: (public_key, secret_key)
        """
        pass

    @abc.abstractmethod
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes, PQCResult]:
        """
        Encapsulates a shared secret for the given public key.

        Args:
            public_key: The public key bytes.

        Returns:
            Tuple[bytes, bytes, PQCResult]: (ciphertext, shared_secret, metadata)
        """
        pass

    @abc.abstractmethod
    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """
        Decapsulates the shared secret from the ciphertext using the secret key.

        Args:
            ciphertext: The encapsulated ciphertext bytes.
            secret_key: The private key bytes.

        Returns:
            bytes: The shared secret.
        """
        pass
