"""Bootstrap — ordered startup for live cognitive OS."""

from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class OdinBootstrap:
    """On startup: restore state, wire router, start buses and loops."""

    async def boot(self, app: Any) -> dict[str, Any]:
        report: dict[str, Any] = {"steps": []}

        def record(step: str, ok: bool = True, detail: dict | None = None) -> None:
            report["steps"].append({"step": step, "ok": ok, **(detail or {})})

        # 1 kernel state
        state = app.kernel.get_state()
        record("load_kernel_state", detail={"signal_count": state.signal_count})

        # 2 snapshot restore
        if app.settings.bootstrap_restore_snapshot:
            snaps = app.snapshots.list_snapshots()
            if snaps:
                latest = snaps[-1]
                try:
                    snap = app.snapshots.restore_snapshot(latest.id)
                    if snap and snap.kernel_state:
                        from odin_backend.core.kernel.state import CognitiveState

                        app.kernel.commit_state(CognitiveState.model_validate(snap.kernel_state))
                    record("restore_snapshot", detail={"snapshot_id": latest.id})
                except Exception as exc:
                    record("restore_snapshot", ok=False, detail={"error": str(exc)})
            else:
                record("restore_snapshot", detail={"skipped": "no snapshots"})
        else:
            record("restore_snapshot", detail={"skipped": "disabled"})

        # 3 model router
        app.kernel.set_model_router(app.model_router)
        record("initialize_model_router")

        # 4 governor + coherence (idempotent)
        app.governor.set_kernel(app.kernel)
        app.governor.set_autonomy(app.autonomy)
        app.governor.set_coherence(app.coherence)
        record("activate_governor")

        # 5 mission restore
        if getattr(app.settings, "mission_restore_on_startup", True):
            try:
                await app.mission_manager.connect()
                restored = await app.mission_manager.restore_active()
                record("restore_missions", detail={"count": len(restored)})
            except Exception as exc:
                record("restore_missions", ok=False, detail={"error": str(exc)})

        report["booted"] = True
        logger.info("odin_bootstrap_complete", steps=len(report["steps"]))
        return report
