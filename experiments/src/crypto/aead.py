import os
import time
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AEAD:
    """
    Provides AES-256-GCM authenticated encryption for the baselines.
    """
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("AES-256-GCM requires a 32-byte key")
        self.aesgcm = AESGCM(key)
        
    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes, float]:
        """
        Encrypts plaintext using a random 12-byte nonce.
        Returns (nonce, ciphertext, elapsed_ms)
        """
        start = time.perf_counter()
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
        end = time.perf_counter()
        
        return nonce, ciphertext, (end - start) * 1000.0
        
    def decrypt(self, nonce: bytes, ciphertext: bytes, associated_data: bytes = None) -> Tuple[bytes, float]:
        """
        Decrypts ciphertext.
        Returns (plaintext, elapsed_ms)
        """
        start = time.perf_counter()
        try:
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, associated_data)
        except Exception as e:
            raise ValueError("AEAD Decryption Failed") from e
        end = time.perf_counter()
        
        return plaintext, (end - start) * 1000.0
