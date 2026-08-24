import time
import random
from typing import Any
from experiments.src.baselines.baseline_interface import BaselineProtocol, BaselineResult
from experiments.src.crypto.classical_baseline import ClassicalBaselineCrypto
from experiments.src.crypto.kdf import ClassicalKDF
from experiments.src.crypto.aead import AEAD

class B1Classical(BaselineProtocol):
    """
    B1: Pre-quantum baseline using X25519 + Ed25519 + AES-256-GCM.
    """
    def __init__(self):
        self.mode = "CLASSICAL"
        
    def initialize(self, seed: int, **kwargs):
        self.rng = random.Random(seed)
        
    def execute_transaction(self, payload: bytes, qkd_pool: Any = None) -> BaselineResult:
        total_crypto_time = 0.0
        msg_overhead = 0
        
        # 1. Key Establishment (X25519)
        pub_a, priv_a = ClassicalBaselineCrypto.generate_x25519_keypair()
        pub_b, priv_b = ClassicalBaselineCrypto.generate_x25519_keypair()
        msg_overhead += len(pub_a) + len(pub_b)
        
        shared_secret, ke_time = ClassicalBaselineCrypto.x25519_exchange(priv_a, pub_b)
        total_crypto_time += ke_time
        
        # KDF
        session_key, kdf_time = ClassicalKDF.derive_key(shared_secret)
        total_crypto_time += kdf_time
        
        # 2. Authentication (Ed25519)
        # Sign the ephemeral public keys to authenticate the exchange
        auth_pub, auth_priv = ClassicalBaselineCrypto.generate_ed25519_keypair()
        msg_to_sign = pub_a + pub_b
        
        signature, sign_time = ClassicalBaselineCrypto.ed25519_sign(msg_to_sign, auth_priv)
        total_crypto_time += sign_time
        msg_overhead += len(signature) + len(auth_pub)
        
        success, verify_time = ClassicalBaselineCrypto.ed25519_verify(signature, msg_to_sign, auth_pub)
        total_crypto_time += verify_time
        
        if not success:
            return BaselineResult(
                success=False,
                selected_mode=self.mode,
                failure_reason="Authentication Failed"
            )
            
        # 3. Encryption (AES-GCM)
        aead = AEAD(session_key)
        nonce, ciphertext, enc_time = aead.encrypt(payload)
        total_crypto_time += enc_time
        msg_overhead += len(nonce) + 16 # GCM tag overhead
        
        # Decryption check
        _, dec_time = aead.decrypt(nonce, ciphertext)
        total_crypto_time += dec_time
        
        return BaselineResult(
            success=True,
            selected_mode=self.mode,
            key_establishment_latency_ms=ke_time + kdf_time,
            authentication_latency_ms=sign_time + verify_time,
            encryption_latency_ms=enc_time + dec_time,
            total_crypto_latency_ms=total_crypto_time,
            payload_bytes=len(payload),
            message_overhead_bytes=msg_overhead
        )
