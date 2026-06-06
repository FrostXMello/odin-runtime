"""Deployment orchestrator."""

from __future__ import annotations

import platform
from typing import Any

from odin_backend.deployment.backup_restore import BackupRestore
from odin_backend.deployment.config_profiles import profile_config
from odin_backend.deployment.dependency_manager import check_dependencies
from odin_backend.deployment.environment_validator import validate_environment
from odin_backend.deployment.first_boot_setup import first_boot_state
from odin_backend.deployment.hardware_detector import detect_hardware
from odin_backend.deployment.update_manager import migrate


class DeploymentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._backup = BackupRestore()
        self._profile = "balanced"
        self._bootstrapped = False

    async def validate(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "deployment_enabled", False):
            return {"accepted": False, "reason": "deployment_disabled"}
        env = validate_environment()
        deps = check_dependencies()
        hw = detect_hardware(
            ram_mb=getattr(self._app.settings, "local_ai_ram_mb", 16384),
            vram_mb=getattr(self._app.settings, "local_ai_vram_mb", 4096),
        )
        valid = env["valid"] and deps["satisfied"]
        self._emit("deployment_validated", {"valid": valid, "profile": hw["recommended_profile"]})
        return {"accepted": True, "valid": valid, "environment": env, "dependencies": deps, "hardware": hw}

    async def bootstrap(self, *, profile: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "deployment_enabled", False):
            return {"accepted": False, "reason": "deployment_disabled"}
        validation = await self.validate()
        hw = validation.get("hardware", {})
        chosen = profile or hw.get("recommended_profile", "balanced")
        self._profile = chosen
        config = profile_config(chosen)
        boot = first_boot_state(profile=chosen)
        self._bootstrapped = True
        self._emit("runtime_profile_changed", {"profile": chosen, "config": config})
        return {"accepted": True, "profile": chosen, "config": config, "first_boot": boot, "platform": platform.system()}

    async def export_snapshot(self) -> dict[str, Any]:
        state = self._collect_state()
        exported = self._backup.export_state(state)
        return {"accepted": True, **exported}

    async def restore_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        state = self._backup.import_state(snapshot_id)
        if not state:
            return {"accepted": False, "reason": "snapshot_not_found"}
        self._emit("snapshot_restored", {"snapshot_id": snapshot_id})
        return {"accepted": True, "state": state}

    async def upgrade(self, *, to_version: str) -> dict[str, Any]:
        from_version = getattr(self._app.settings, "app_version", "0.1.0")
        result = migrate(from_version, to_version)
        return {"accepted": True, **result}

    def snapshot(self) -> dict[str, Any]:
        return {
            "profile": self._profile,
            "bootstrapped": self._bootstrapped,
            "snapshots": len(self._backup.list_snapshots()),
            "platform": platform.system(),
        }

    def _collect_state(self) -> dict[str, Any]:
        state: dict[str, Any] = {"profile": self._profile}
        if hasattr(self._app, "project_os"):
            state["projects"] = self._app.project_os.snapshot()
        if hasattr(self._app, "runtime_guardian"):
            state["guardian"] = self._app.runtime_guardian.snapshot()
        return state

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="deployment")
