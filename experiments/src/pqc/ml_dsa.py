import time
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import mldsa

class MLDSASigner:
    """
    ML-DSA adapter wrapping the cryptography library implementation.
    """
    def __init__(self, parameter_set: str = "ML-DSA-65"):
        self.parameter_set = parameter_set
        
        if parameter_set == "ML-DSA-44":
            self._key_class = mldsa.MLDSA44PrivateKey
            self._pub_class = mldsa.MLDSA44PublicKey
            self.public_key_length = 1312
            self.signature_length = 2420
        elif parameter_set == "ML-DSA-65":
            self._key_class = mldsa.MLDSA65PrivateKey
            self._pub_class = mldsa.MLDSA65PublicKey
            self.public_key_length = 1952
            self.signature_length = 3309
        elif parameter_set == "ML-DSA-87":
            self._key_class = mldsa.MLDSA87PrivateKey
            self._pub_class = mldsa.MLDSA87PublicKey
            self.public_key_length = 2592
            self.signature_length = 4627
        else:
            raise ValueError(f"Unsupported ML-DSA parameter set: {parameter_set}")
            
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generates public and private key material."""
        priv_key = self._key_class.generate()
        pub_key = priv_key.public_key()
        return pub_key.public_bytes_raw(), priv_key.private_bytes_raw()
        
    def sign(self, message: bytes, private_key: bytes) -> Tuple[bytes, float]:
        """
        Signs the message and returns the signature and operation time (ms).
        """
        start = time.perf_counter()
        priv = self._key_class.from_seed_bytes(private_key)
        signature = priv.sign(message)
        end = time.perf_counter()
        return signature, (end - start) * 1000.0
        
    def verify(self, signature: bytes, message: bytes, public_key: bytes) -> Tuple[bool, float]:
        """
        Verifies the signature and returns success and operation time (ms).
        """
        start = time.perf_counter()
        try:
            pub = self._pub_class.from_public_bytes(public_key)
            pub.verify(signature, message)
            success = True
        except Exception:
            success = False
        end = time.perf_counter()
        return success, (end - start) * 1000.0
