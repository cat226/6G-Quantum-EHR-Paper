import time
import random
from typing import Any
from experiments.src.baselines.baseline_interface import BaselineProtocol, BaselineResult
from src.pqc.ml_kem import MLKEMProtocol
from experiments.src.pqc.ml_dsa import MLDSASigner
from experiments.src.crypto.aead import AEAD
from experiments.src.crypto.kdf import ClassicalKDF

class B2PQCOnly(BaselineProtocol):
    """
    B2: PQC-only baseline using ML-KEM-768 + ML-DSA-65 + AES-256-GCM.
    """
    def __init__(self):
        self.mode = "PQC_ONLY"
        self.kem = MLKEMProtocol(parameter_set="ML-KEM-768")
        self.dsa = MLDSASigner(parameter_set="ML-DSA-65")
        
    def initialize(self, seed: int, **kwargs):
        self.rng = random.Random(seed)
        
    def execute_transaction(self, payload: bytes, qkd_pool: Any = None) -> BaselineResult:
        total_crypto_time = 0.0
        msg_overhead = 0
        
        # 1. Key Establishment (ML-KEM)
        start = time.perf_counter()
        pub_b, priv_b = self.kem.generate_keypair()
        ciphertext, shared_secret_a, _ = self.kem.encapsulate(pub_b)
        shared_secret_b = self.kem.decapsulate(ciphertext, priv_b)
        end = time.perf_counter()
        ke_time = (end - start) * 1000.0
        total_crypto_time += ke_time
        
        msg_overhead += len(pub_b) + len(ciphertext)
        
        # KDF to 32 bytes for AES
        session_key, kdf_time = ClassicalKDF.derive_key(shared_secret_a)
        total_crypto_time += kdf_time
        
        # 2. Authentication (ML-DSA)
        # Sign the KEM ciphertext to authenticate the exchange
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
            key_establishment_latency_ms=ke_time + kdf_time,
            authentication_latency_ms=sign_time + verify_time,
            encryption_latency_ms=enc_time + dec_time,
            total_crypto_latency_ms=total_crypto_time,
            payload_bytes=len(payload),
            message_overhead_bytes=msg_overhead
        )
