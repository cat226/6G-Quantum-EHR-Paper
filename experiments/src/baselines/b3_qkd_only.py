import time
import random
import os
from typing import Any
from experiments.src.baselines.baseline_interface import BaselineProtocol, BaselineResult
from experiments.src.pqc.ml_dsa import MLDSASigner
from experiments.src.crypto.aead import AEAD
from experiments.src.crypto.kdf import ClassicalKDF
from experiments.src.qkd_model.qkd_pool import QKDPool

class B3QKDOnly(BaselineProtocol):
    """
    B3: QKD-only baseline using QKD key + ML-DSA-65 + AES-256-GCM.
    Fails/blocks if QKD is unavailable.
    """
    def __init__(self):
        self.mode = "QKD_ONLY"
        self.dsa = MLDSASigner(parameter_set="ML-DSA-65")
        
    def initialize(self, seed: int, **kwargs):
        self.rng = random.Random(seed)
        
    def execute_transaction(self, payload: bytes, qkd_pool: Any = None) -> BaselineResult:
        if not isinstance(qkd_pool, QKDPool):
            raise ValueError("B3 requires a valid QKDPool")
            
        total_crypto_time = 0.0
        msg_overhead = 0
        
        # 1. Key Establishment (QKD)
        # Attempt to consume 256 bits (32 bytes) from the pool
        start = time.perf_counter()
        if not qkd_pool.debit(256):
            return BaselineResult(
                success=False,
                selected_mode=self.mode,
                failure_reason="QKD Material Unavailable"
            )
            
        # We simulate the key generation by just using a random 32-byte string
        # since we don't need actual BB84 execution inside the simulation loop
        # per the guidelines (it's abstracted out by the QKDPool).
        # We just need to track the time. BB84 execution time is usually large but
        # here we assume key is drawn from the pool which is near-instantaneous,
        # but we add a nominal fetch latency.
        time.sleep(0.0001) 
        qkd_key = os.urandom(32)
        end = time.perf_counter()
        ke_time = (end - start) * 1000.0
        total_crypto_time += ke_time
        
        # KDF to derive AES key
        session_key, kdf_time = ClassicalKDF.derive_key(qkd_key, length=32)
        total_crypto_time += kdf_time
        
        # 2. Authentication (ML-DSA)
        # Since QKD requires an authenticated classical channel, we sign a dummy nonce
        auth_pub, auth_priv = self.dsa.generate_keypair()
        sync_nonce = os.urandom(16)
        
        signature, sign_time = self.dsa.sign(sync_nonce, auth_priv)
        total_crypto_time += sign_time
        
        success, verify_time = self.dsa.verify(signature, sync_nonce, auth_pub)
        total_crypto_time += verify_time
        
        msg_overhead += len(auth_pub) + len(signature) + len(sync_nonce)
        
        if not success:
            return BaselineResult(
                success=False,
                selected_mode=self.mode,
                failure_reason="Authentication Failed"
            )
            
        # 3. Encryption (AES-GCM)
        aead = AEAD(session_key)
        nonce, enc_ciphertext, enc_time = aead.encrypt(payload)
        total_crypto_time += enc_time
        msg_overhead += len(nonce) + 16 # GCM tag
        
        # Decrypt check
        _, dec_time = aead.decrypt(nonce, enc_ciphertext)
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
