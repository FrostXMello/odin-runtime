"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from odin_backend.api.routes import (
    agents,
    browser,
    cognition,
    context,
    conversation,
    events,
    health,
    knowledge_graph,
    memory,
    missions,
    perception,
    adaptive_runtime,
    objectives,
    observability,
    permissions,
    personalization,
    persistent_workflows,
    context_engine,
    ambient,
    desktop_runtime,
    environment,
    kernel,
    stability,
    protocol,
    conscious_loop,
    live_runtime,
    valkyrie,
    reflection,
    runtime,
    runtime_diagnostics,
    runtime_observability,
    distributed_runtime,
    planner_runtime,
    cognition_runtime,
    models_runtime,
    autonomy_runtime,
    multimodal_runtime,
    action_runtime,
    knowledge_runtime,
    society_runtime,
    federation_runtime,
    infrastructure_runtime,
    production_runtime,
    reliability_runtime,
    personal_os_runtime,
    daily_driver_runtime,
    intelligence_refinement_runtime,
    engineering_workspace_runtime,
    cognitive_workstation_runtime,
    cognitive_interface_runtime,
    self_evolution_runtime,
    native_desktop_runtime,
    persistent_environment_runtime,
    desktop_experience_runtime,
    unified_cognitive_runtime,
    engineering_workstation_runtime,
    cognitive_computer_runtime,
    adaptive_autonomous_os_runtime,
    real_autonomous_cognitive_os_runtime,
    cognitive_infrastructure_runtime,
    unified_cognitive_core_runtime,
    autonomous_overnight_cognition_runtime,
    native_autonomous_desktop_runtime,
    autonomous_cognitive_coordination_runtime,
    live_cognitive_orchestration_runtime,
    operational_execution_system_runtime,
    distributed_cognitive_execution_runtime,
    predictive_cognitive_governance_runtime,
    unified_cognitive_command_center_runtime,
    traces,
    ws,
    executions,
    sandbox,
    tasks,
    tools,
    voice,
    watchers,
    workflows,
)
from odin_backend.core.app import OdinApplication


def create_api(odin_app: OdinApplication | None = None) -> FastAPI:
    odin = odin_app or OdinApplication()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.odin = odin
        await odin.startup()
        yield
        await odin.shutdown()

    app = FastAPI(
        title=odin.settings.app_name,
        version=odin.settings.app_version,
        description="PROJECT ODIN — Autonomous AI Operating System",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(agents.router, prefix="/api/v1")
    app.include_router(tools.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(objectives.router, prefix="/api/v1")
    app.include_router(missions.router, prefix="/api/v1")
    app.include_router(perception.router, prefix="/api/v1")
    app.include_router(adaptive_runtime.router, prefix="/api/v1")
    app.include_router(workflows.router, prefix="/api/v1")
    app.include_router(events.router, prefix="/api/v1")
    app.include_router(permissions.router, prefix="/api/v1")
    app.include_router(observability.router, prefix="/api/v1")
    app.include_router(runtime.router, prefix="/api/v1")
    app.include_router(runtime_diagnostics.router, prefix="/api/v1")
    app.include_router(runtime_observability.router, prefix="/api/v1")
    app.include_router(distributed_runtime.router, prefix="/api/v1")
    app.include_router(planner_runtime.router, prefix="/api/v1")
    app.include_router(cognition_runtime.router, prefix="/api/v1")
    app.include_router(models_runtime.router, prefix="/api/v1")
    app.include_router(autonomy_runtime.router, prefix="/api/v1")
    app.include_router(multimodal_runtime.router, prefix="/api/v1")
    app.include_router(action_runtime.router, prefix="/api/v1")
    app.include_router(knowledge_runtime.router, prefix="/api/v1")
    app.include_router(society_runtime.router, prefix="/api/v1")
    app.include_router(federation_runtime.router, prefix="/api/v1")
    app.include_router(infrastructure_runtime.router, prefix="/api/v1")
    app.include_router(production_runtime.router, prefix="/api/v1")
    app.include_router(reliability_runtime.router, prefix="/api/v1")
    app.include_router(personal_os_runtime.router, prefix="/api/v1")
    app.include_router(daily_driver_runtime.router, prefix="/api/v1")
    app.include_router(intelligence_refinement_runtime.router, prefix="/api/v1")
    app.include_router(engineering_workspace_runtime.router, prefix="/api/v1")
    app.include_router(cognitive_workstation_runtime.router, prefix="/api/v1")
    app.include_router(cognitive_interface_runtime.router, prefix="/api/v1")
    app.include_router(self_evolution_runtime.router, prefix="/api/v1")
    app.include_router(native_desktop_runtime.router, prefix="/api/v1")
    app.include_router(persistent_environment_runtime.router, prefix="/api/v1")
    app.include_router(desktop_experience_runtime.router, prefix="/api/v1")
    app.include_router(unified_cognitive_runtime.router, prefix="/api/v1")
    app.include_router(engineering_workstation_runtime.router, prefix="/api/v1")
    app.include_router(cognitive_computer_runtime.router, prefix="/api/v1")
    app.include_router(adaptive_autonomous_os_runtime.router, prefix="/api/v1")
    app.include_router(real_autonomous_cognitive_os_runtime.router, prefix="/api/v1")
    app.include_router(cognitive_infrastructure_runtime.router, prefix="/api/v1")
    app.include_router(unified_cognitive_core_runtime.router, prefix="/api/v1")
    app.include_router(autonomous_overnight_cognition_runtime.router, prefix="/api/v1")
    app.include_router(native_autonomous_desktop_runtime.router, prefix="/api/v1")
    app.include_router(autonomous_cognitive_coordination_runtime.router, prefix="/api/v1")
    app.include_router(live_cognitive_orchestration_runtime.router, prefix="/api/v1")
    app.include_router(operational_execution_system_runtime.router, prefix="/api/v1")
    app.include_router(distributed_cognitive_execution_runtime.router, prefix="/api/v1")
    app.include_router(predictive_cognitive_governance_runtime.router, prefix="/api/v1")
    app.include_router(unified_cognitive_command_center_runtime.router, prefix="/api/v1")
    app.include_router(traces.router, prefix="/api/v1")
    app.include_router(ws.router, prefix="/api/v1")
    app.include_router(executions.router, prefix="/api/v1")
    app.include_router(browser.router, prefix="/api/v1")
    app.include_router(cognition.router, prefix="/api/v1")
    app.include_router(context.router, prefix="/api/v1")
    app.include_router(voice.router, prefix="/api/v1")
    app.include_router(watchers.router, prefix="/api/v1")
    app.include_router(conversation.router, prefix="/api/v1")
    app.include_router(knowledge_graph.router, prefix="/api/v1")
    app.include_router(sandbox.router, prefix="/api/v1")
    app.include_router(persistent_workflows.router, prefix="/api/v1")
    app.include_router(reflection.router, prefix="/api/v1")
    app.include_router(personalization.router, prefix="/api/v1")
    app.include_router(context_engine.router, prefix="/api/v1")
    app.include_router(ambient.router, prefix="/api/v1")
    app.include_router(desktop_runtime.router, prefix="/api/v1")
    app.include_router(environment.router, prefix="/api/v1")
    app.include_router(kernel.router, prefix="/api/v1")
    app.include_router(stability.router, prefix="/api/v1")
    app.include_router(protocol.router, prefix="/api/v1")
    app.include_router(conscious_loop.router, prefix="/api/v1")
    app.include_router(live_runtime.router, prefix="/api/v1")
    app.include_router(valkyrie.router, prefix="/api/v1")

    return app
