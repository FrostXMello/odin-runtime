"""MIMIR memory layer."""

from odin_backend.memory.coordinator import MimirCoordinator

# Backward compatibility alias
MemoryService = MimirCoordinator

__all__ = ["MimirCoordinator", "MemoryService"]
