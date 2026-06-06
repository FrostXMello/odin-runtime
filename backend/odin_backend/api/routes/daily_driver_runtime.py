"""Daily driver runtime APIs (Prompt 37)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["daily-driver-runtime"])


class BootstrapRequest(BaseModel):
    profile: str | None = None


class CommandRequest(BaseModel):
    command: str


class RestoreSnapshotRequest(BaseModel):
    snapshot_id: str


class UpgradeRequest(BaseModel):
    to_version: str


class FilterTextRequest(BaseModel):
    text: str


class PermissionCheckRequest(BaseModel):
    action: str
    approved: bool = False


class DaemonModeRequest(BaseModel):
    mode: str


class LocalAIModeRequest(BaseModel):
    mode: str


@router.get("/deployment")
async def runtime_deployment(request: Request) -> dict:
    app = request.app.state.odin
    return {"deployment": app.deployment.snapshot()}


@router.post("/deployment/validate")
async def runtime_deployment_validate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.deployment.validate()


@router.post("/deployment/bootstrap")
async def runtime_deployment_bootstrap(body: BootstrapRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.deployment.bootstrap(profile=body.profile)


@router.post("/deployment/export")
async def runtime_deployment_export(request: Request) -> dict:
    app = request.app.state.odin
    return await app.deployment.export_snapshot()


@router.post("/deployment/restore")
async def runtime_deployment_restore(body: RestoreSnapshotRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.deployment.restore_snapshot(body.snapshot_id)


@router.post("/deployment/upgrade")
async def runtime_deployment_upgrade(body: UpgradeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.deployment.upgrade(to_version=body.to_version)


@router.get("/performance")
async def runtime_performance(request: Request) -> dict:
    app = request.app.state.odin
    return {"performance": app.performance.snapshot()}


@router.post("/performance/optimize")
async def runtime_performance_optimize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.performance.optimize()


@router.post("/performance/startup")
async def runtime_performance_startup(request: Request) -> dict:
    app = request.app.state.odin
    return await app.performance.optimize_startup()


@router.get("/privacy")
async def runtime_privacy(request: Request) -> dict:
    app = request.app.state.odin
    return {"privacy": app.privacy.snapshot()}


@router.post("/privacy/filter")
async def runtime_privacy_filter(body: FilterTextRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.privacy.filter_text(body.text)


@router.post("/privacy/check")
async def runtime_privacy_check(body: PermissionCheckRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.privacy.check(action=body.action, approved=body.approved)


@router.get("/command-center")
async def runtime_command_center(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "shell": app.operator_shell.snapshot(),
        "quick_actions": app.operator_shell.quick_actions(),
        "shortcuts": app.operator_shell.shortcuts(),
    }


@router.post("/command-center/execute")
async def runtime_command_execute(body: CommandRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_shell.execute(body.command)


@router.get("/activity")
async def runtime_activity(request: Request) -> dict:
    app = request.app.state.odin
    routine = await app.daily_workflow.startup_routine()
    return {
        "daily_workflow": app.daily_workflow.snapshot(),
        "startup": routine,
        "shell_history": app.operator_shell.snapshot(),
    }


@router.post("/activity/consolidate")
async def runtime_activity_consolidate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_workflow.idle_consolidation()


@router.get("/diagnostics")
async def runtime_diagnostics_panel(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_guardian.recovery_report()


@router.get("/recovery-report")
async def runtime_recovery_report(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_guardian.recovery_report()


@router.post("/recovery/safe-boot")
async def runtime_safe_boot(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_guardian.safe_boot()


@router.get("/updates")
async def runtime_updates(request: Request) -> dict:
    app = request.app.state.odin
    return {"deployment": app.deployment.snapshot(), "version": app.settings.app_version}


@router.post("/daemon/mode")
async def runtime_daemon_mode(body: DaemonModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.set_mode(body.mode)


@router.post("/daemon/watchdog-restart")
async def runtime_daemon_watchdog(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.watchdog_restart()


@router.post("/local-ai/mode")
async def runtime_local_ai_mode(body: LocalAIModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.local_ai.set_mode(body.mode)


@router.get("/storage/analytics")
async def runtime_storage_analytics(request: Request) -> dict:
    app = request.app.state.odin
    return {"analytics": await app.storage_optimization.analytics()}
