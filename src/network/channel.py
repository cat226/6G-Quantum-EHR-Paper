"""
Re-exports NetworkLink as the "channel" abstraction requested by Task 8
Phase 2's file layout. The actual implementation lives in topology.py
alongside Topology/NetworkParameters, since a channel/link is
meaningless without the topology conventions it's used in (hop count,
which segment it represents). See docs/implementation_notes.md's
"Structural deviations from Task 8 Phase 2" note for the rationale.
"""

from .topology import NetworkLink, NetworkParameters  # noqa: F401
