import time
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives import serialization

class ClassicalBaselineCrypto:
    """
    Implements X25519 for key establishment and Ed25519 for authentication.
    """
    
    # --- X25519 ---
    @staticmethod
    def generate_x25519_keypair() -> Tuple[bytes, bytes]:
        priv = x25519.X25519PrivateKey.generate()
        pub = priv.public_key()
        return pub.public_bytes_raw(), priv.private_bytes_raw()
        
    @staticmethod
    def x25519_exchange(private_key: bytes, peer_public_key: bytes) -> Tuple[bytes, float]:
        start = time.perf_counter()
        priv = x25519.X25519PrivateKey.from_private_bytes(private_key)
        pub = x25519.X25519PublicKey.from_public_bytes(peer_public_key)
        shared_secret = priv.exchange(pub)
        end = time.perf_counter()
        return shared_secret, (end - start) * 1000.0

    # --- Ed25519 ---
    @staticmethod
    def generate_ed25519_keypair() -> Tuple[bytes, bytes]:
        priv = ed25519.Ed25519PrivateKey.generate()
        pub = priv.public_key()
        return pub.public_bytes_raw(), priv.private_bytes_raw()
        
    @staticmethod
    def ed25519_sign(message: bytes, private_key: bytes) -> Tuple[bytes, float]:
        start = time.perf_counter()
        priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        signature = priv.sign(message)
        end = time.perf_counter()
        return signature, (end - start) * 1000.0
        
    @staticmethod
    def ed25519_verify(signature: bytes, message: bytes, public_key: bytes) -> Tuple[bool, float]:
        start = time.perf_counter()
        try:
            pub = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            pub.verify(signature, message)
            success = True
        except Exception:
            success = False
        end = time.perf_counter()
        return success, (end - start) * 1000.0
