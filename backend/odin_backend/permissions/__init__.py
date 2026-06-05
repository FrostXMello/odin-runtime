"""Security and permission enforcement."""

from odin_backend.permissions.models import PermissionClass, PermissionDecision
from odin_backend.permissions.service import PermissionService

__all__ = ["PermissionClass", "PermissionDecision", "PermissionService"]


def __getattr__(name: str):
    if name in ("HeimdallService", "PermissionRequest"):
        from odin_backend.permissions.heimdall import HeimdallService, PermissionRequest
        return {"HeimdallService": HeimdallService, "PermissionRequest": PermissionRequest}[name]
    raise AttributeError(name)
