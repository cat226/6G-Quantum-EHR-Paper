import time
import random
import os
from typing import Any
from experiments.src.baselines.baseline_interface import BaselineProtocol, BaselineResult
from src.pqc.ml_kem import MLKEMProtocol
from experiments.src.pqc.ml_dsa import MLDSASigner
from experiments.src.crypto.aead import AEAD
from experiments.src.crypto.kdf import HybridKDF
from experiments.src.qkd_model.qkd_pool import QKDPool

class B4StaticHybrid(BaselineProtocol):
    """
    B4: Static Hybrid baseline using QKD + ML-KEM-768 + ML-DSA-65 + AES-256-GCM.
    Fails/blocks if QKD is unavailable.
    """
    def __init__(self):
        self.mode = "HYBRID"
        self.kem = MLKEMProtocol(parameter_set="ML-KEM-768")
        self.dsa = MLDSASigner(parameter_set="ML-DSA-65")
        
    def initialize(self, seed: int, **kwargs):
        self.rng = random.Random(seed)
        
    def execute_transaction(self, payload: bytes, qkd_pool: Any = None) -> BaselineResult:
        if not isinstance(qkd_pool, QKDPool):
            raise ValueError("B4 requires a valid QKDPool")
            
        total_crypto_time = 0.0
        msg_overhead = 0
        
        # 1. Key Establishment (QKD + ML-KEM)
        start = time.perf_counter()
        if not qkd_pool.debit(256):
            return BaselineResult(
                success=False,
                selected_mode=self.mode,
                failure_reason="QKD Material Unavailable"
            )
            
        # Draw from pool
        time.sleep(0.0001)
        qkd_key = os.urandom(32)
        end = time.perf_counter()
        ke_qkd_time = (end - start) * 1000.0
        
        # ML-KEM exchange
        start = time.perf_counter()
        pub_b, priv_b = self.kem.generate_keypair()
        ciphertext, shared_secret_a, _ = self.kem.encapsulate(pub_b)
        shared_secret_b = self.kem.decapsulate(ciphertext, priv_b)
        end = time.perf_counter()
        ke_kem_time = (end - start) * 1000.0
        
        total_crypto_time += ke_qkd_time + ke_kem_time
        msg_overhead += len(pub_b) + len(ciphertext)
        
        # Hybrid KDF
        session_key, kdf_time = HybridKDF.derive_hybrid_key(k_qkd=qkd_key, k_pqc=shared_secret_a)
        total_crypto_time += kdf_time
        
        # 2. Authentication (ML-DSA)
        auth_pub, auth_priv = self.dsa.generate_keypair()
        signature, sign_time = self.dsa.sign(ciphertext, auth_priv)
        total_crypto_time += sign_time
        
        success, verify_time = self.dsa.verify(signature, ciphertext, auth_pub)
        total_crypto_time += verify_time
        msg_overhead += len(auth_pub) + len(signature)
        
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
            key_establishment_latency_ms=ke_qkd_time + ke_kem_time + kdf_time,
            authentication_latency_ms=sign_time + verify_time,
            encryption_latency_ms=enc_time + dec_time,
            total_crypto_latency_ms=total_crypto_time,
            payload_bytes=len(payload),
            message_overhead_bytes=msg_overhead
        )
