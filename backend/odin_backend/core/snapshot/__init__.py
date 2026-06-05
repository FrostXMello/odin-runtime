"""Global state snapshots — capture, restore, diff."""

from odin_backend.core.snapshot.engine import SnapshotEngine, SystemSnapshot

__all__ = ["SnapshotEngine", "SystemSnapshot"]
