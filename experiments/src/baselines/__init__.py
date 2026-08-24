from .baseline_interface import BaselineProtocol, BaselineResult
from .b1_classical import B1Classical
from .b2_pqc_only import B2PQCOnly
from .b3_qkd_only import B3QKDOnly
from .b4_static_hybrid import B4StaticHybrid
from .b5_adaptive import B5Adaptive

def get_baseline(name: str) -> BaselineProtocol:
    mapping = {
        "B1": B1Classical,
        "B2": B2PQCOnly,
        "B3": B3QKDOnly,
        "B4": B4StaticHybrid,
        "B5": B5Adaptive
    }
    if name not in mapping:
        raise ValueError(f"Unknown baseline: {name}")
    return mapping[name]()
