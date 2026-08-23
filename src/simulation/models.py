from dataclasses import dataclass
from enum import Enum
from typing import Dict

class EntityRole(Enum):
    SENDER = 'SENDER'
    RECEIVER = 'RECEIVER'
    EDGE_NODE = 'EDGE_NODE'
    MEDICAL_DEVICE = 'MEDICAL_DEVICE'
    KEY_MANAGER = 'KEY_MANAGER'

@dataclass
class Entity:
    entity_id: str
    role: EntityRole
    properties: Dict[str, str]

    def __post_init__(self):
        if not self.entity_id:
            raise ValueError('entity_id must not be empty')
        if not isinstance(self.role, EntityRole):
            raise ValueError('role must be an EntityRole')

@dataclass
class NetworkCondition:
    propagation_latency_ms: float
    bandwidth_mbps: float
    packet_loss_rate: float
    congestion_level: float
    edge_processing_delay_ms: float
    qkd_availability_status: str
    key_material_availability: bool

    def __post_init__(self):
        if self.propagation_latency_ms < 0:
            raise ValueError('Latency cannot be negative')
        if self.bandwidth_mbps < 0:
            raise ValueError('Bandwidth cannot be negative')
        if not (0.0 <= self.packet_loss_rate <= 1.0):
            raise ValueError('Packet loss rate must be between 0 and 1')
        if self.congestion_level < 0:
            raise ValueError('Congestion level cannot be negative')
        if self.edge_processing_delay_ms < 0:
            raise ValueError('Edge processing delay cannot be negative')

@dataclass
class EHRTransmission:
    transmission_id: str
    source_entity_id: str
    destination_entity_id: str
    payload_size_bytes: int
    timestamp_sequence: int
    security_mode_id: str

    def __post_init__(self):
        if self.timestamp_sequence < 0:
            raise ValueError('Timestamp sequence cannot be negative')
        if self.payload_size_bytes <= 0:
            raise ValueError('Payload size must be positive')
        if not self.transmission_id or not self.source_entity_id or not self.destination_entity_id:
            raise ValueError('IDs must not be empty')
