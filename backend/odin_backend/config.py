"""Application configuration via environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global ODIN backend settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ODIN_",
        extra="ignore",
    )

    app_name: str = "PROJECT ODIN"
    app_version: str = "0.1.0"
    debug: bool = False
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    redis_url: str = "redis://127.0.0.1:6379/0"
    redis_event_channel: str = "odin:events"
    redis_task_queue: str = "odin:tasks"

    database_url: str = "sqlite+aiosqlite:///./data/odin.db"
    chroma_persist_dir: Path = Field(default=Path("./data/chroma"))

    log_level: str = "INFO"
    log_json: bool = False
    log_dir: Path = Field(default=Path("./logs"))

    openai_api_key: str | None = None
    orchestrator_max_concurrent_tasks: int = 10
    task_default_timeout_seconds: int = 300

    # Persistent runtime
    runtime_heartbeat_interval_seconds: int = 15
    runtime_health_check_interval_seconds: int = 30
    runtime_enable_background_loops: bool = True

    # Browser CDP
    chrome_cdp_url: str = "http://127.0.0.1:9222"
    browser_enabled: bool = True

    # Context awareness (opt-in)
    context_awareness_enabled: bool = False

    # Voice (push-to-talk only)
    voice_enabled: bool = False
    whisper_model: str = "base"
    piper_voice_path: str | None = None

    # Watchers
    watcher_hugin_interval_seconds: int = 300
    watcher_fafnir_interval_seconds: int = 120
    watcher_heimdall_interval_seconds: int = 60

    # Workflow
    workflow_max_parallel_steps: int = 5

    # Conversation
    conversation_max_turns: int = 100
    conversation_context_token_budget: int = 8000

    # AI routing
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    prefer_local_for_summarization: bool = True

    # Sandbox
    sandbox_work_dir: Path = Field(default=Path("./data/sandbox"))

    # Long-running workflows
    scheduler_enabled: bool = True

    # Ambient layer (Milestone 5)
    proactive_recommendations_enabled: bool = True
    memory_consolidation_interval_hours: int = 24
    local_model_warm_on_startup: bool = False

    # Milestone 6 — live desktop collector
    desktop_collector_enabled: bool = False
    desktop_collector_interval_seconds: int = 5

    # Cognitive stability (Milestone 8)
    stability_loop_enabled: bool = True
    coherence_execution_threshold: float = 0.4
    default_autonomy_level: int = 3  # bounded execution; governor + coherence gate high-risk

    # Milestone 10 — runtime conscious loop
    conscious_loop_enabled: bool = True
    conscious_loop_interval_seconds: float = 3.0
    conscious_loop_stability_interval: int = 10
    conscious_loop_max_executions_per_cycle: int = 2

    # Milestone 11 — live cognitive runtime
    live_loop_enabled: bool = False  # set ODIN_LIVE_LOOP_ENABLED=true for production
    live_loop_interval_seconds: float = 5.0
    live_loop_stability_interval: int = 12
    bootstrap_restore_snapshot: bool = True

    # Milestone 14 — persistent missions
    mission_worker_enabled: bool = False
    mission_dispatch_enabled: bool = True
    mission_dispatch_interval_seconds: float = 2.0
    mission_worker_interval_seconds: float = 3.0
    mission_max_concurrent_missions: int = 3
    mission_max_concurrent_tasks: int = 2
    mission_cooldown_seconds: float = 1.0
    mission_restore_on_startup: bool = True
    mission_restore_max: int = 20
    mission_replay_window_seconds: int = 3600
    mission_stuck_task_seconds: int = 300
    mission_gc_enabled: bool = True
    mission_gc_stale_seconds: int = 7200
    mission_gc_interval_seconds: float = 600.0

    # Real-time streaming (WebSocket)
    streaming_enabled: bool = True
    streaming_heartbeat_interval_seconds: float = 15.0

    # Real execution engine
    execution_engine_enabled: bool = True
    execution_max_concurrent: int = 4
    execution_default_timeout_seconds: float = 120.0
    execution_lease_seconds: float = 300.0
    execution_recovery_interval_seconds: float = 30.0
    execution_stuck_heartbeat_seconds: float = 90.0
    execution_retry_max: int = 3
    execution_retry_backoff_seconds: float = 2.0

    # Mission ↔ execution bridge
    mission_execution_bridge_enabled: bool = True
    async_mission_runtime_enabled: bool = True

    # Persistent distributed queue (Prompt 22)
    queue_persist_enabled: bool = True
    queue_visibility_timeout_seconds: float = 60.0
    queue_max_retries: int = 5
    execution_persist_enabled: bool = True
    distributed_recovery_enabled: bool = True
    worker_id: str | None = None

    # Distributed execution fabric (Prompt 23)
    queue_backend: str = "sqlite"  # sqlite | redis | nats | memory
    redis_mission_queue_key: str = "odin:mq:ready"
    redis_pubsub_channel: str = "odin:runtime:events"
    nats_url: str = "nats://127.0.0.1:4222"
    worker_capabilities: str = "python.safe,shell.safe,workflow.execute,api.internal,filesystem.read,filesystem.write"
    execution_pool_default: str = "local"
    execution_pool_max_concurrent: int = 4
    cognitive_learning_enabled: bool = True
    worker_process_enabled: bool = False

    # Local model cognitive layer (Prompt 26)
    model_provider: str = "mock"  # mock | ollama | llamacpp | mlx
    model_base_url: str = "http://127.0.0.1:11434"
    embedding_model: str = "nomic-embed-text"
    reasoning_model: str = "deepseek-r1:7b"
    fast_model: str = "phi3:mini"
    local_cognition_enabled: bool = True
    reflection_max_depth: int = 2
    reflection_time_budget_seconds: float = 30.0
    max_concurrent_inference: int = 2

    # Autonomous operator mode (Prompt 27)
    autonomous_operator_enabled: bool = False
    autonomy_mode: str = "supervised"
    autonomy_cycle_interval_seconds: float = 60.0
    autonomy_mission_budget_per_hour: int = 5
    autonomy_max_loop_depth: int = 3

    # Multimodal operator intelligence (Prompt 28)
    multimodal_perception_enabled: bool = False
    desktop_awareness_enabled: bool = False
    voice_enabled: bool = False
    copilot_mode: str = "passive_observer"
    whisper_model: str = "base"
    piper_voice_path: str = ""

    # Safe action engine (Prompt 29)
    action_engine_enabled: bool = False
    desktop_automation_enabled: bool = False
    browser_operator_enabled: bool = False
    automation_simulation_mode: bool = True
    approval_mode: str = "manual_every_step"
    overlay_enabled: bool = False
    action_pace_ms: int = 250
    automation_min_gap_ms: int = 100
    automation_max_per_minute: int = 30

    # Knowledge fabric + research (Prompt 30)
    knowledge_fabric_enabled: bool = False
    research_fabric_enabled: bool = False
    web_access_enabled: bool = False
    web_access_allowlist: str = ""
    web_rate_limit_per_minute: int = 20
    web_max_concurrent: int = 2
    web_crawl_max_depth: int = 2
    research_budget_per_hour: int = 10

    # Agent society (Prompt 31)
    agent_society_enabled: bool = False
    agent_society_max_agents: int = 12
    agent_message_rate_per_minute: int = 30
    agent_debate_max_depth: int = 8

    # Federation + world simulation (Prompt 32)
    federation_enabled: bool = False
    federation_node_name: str = "odin-local"
    federation_node_role: str = "coordinator"
    federation_max_nodes: int = 8
    federation_min_trust_share: float = 0.4
    federation_shared_secret: str = "local-only"
    world_simulation_enabled: bool = False
    strategic_reasoning_enabled: bool = False
    simulation_max_branches: int = 5

    # Adaptive infrastructure (Prompt 33)
    runtime_continuity_enabled: bool = False
    background_cognition_enabled: bool = False
    runtime_evolution_enabled: bool = False
    cognitive_economy_enabled: bool = False
    cognitive_economy_mode: str = "balanced"
    meta_reasoning_enabled: bool = False
    operational_planning_enabled: bool = False
    operator_relationship_enabled: bool = False
    distributed_optimization_enabled: bool = False

    # Production runtime (Prompt 34)
    local_ai_enabled: bool = False
    local_ai_vram_mb: int = 4096
    local_ai_ram_mb: int = 16384
    local_ai_warm_on_startup: bool = False
    vector_memory_enabled: bool = False
    agent_execution_enabled: bool = False
    copilot_production_enabled: bool = False
    realtime_voice_enabled: bool = False
    evaluation_enabled: bool = False
    resource_optimization_enabled: bool = False
    resource_mode: str = "normal"
    on_battery: bool = False
    daemon_mode_enabled: bool = False

    # Reliability runtime (Prompt 35)
    runtime_guardian_enabled: bool = False
    self_healing_enabled: bool = False
    real_automation_enabled: bool = False
    automation_mode: str = "simulation"
    memory_consolidation_enabled: bool = False
    survival_mode: str = "balanced"

    # Personal OS (Prompt 36)
    project_os_enabled: bool = False
    developer_integrations_enabled: bool = False
    workspace_knowledge_enabled: bool = False
    productivity_enabled: bool = False
    local_search_enabled: bool = False
    communications_enabled: bool = False
    storage_optimization_enabled: bool = False

    # Daily driver runtime (Prompt 37)
    deployment_enabled: bool = False
    performance_enabled: bool = False
    privacy_enabled: bool = False
    operator_shell_enabled: bool = False
    daily_driver_enabled: bool = False
    local_ai_mode: str = "balanced"

    # Intelligence refinement (Prompt 38)
    intelligence_quality_enabled: bool = False
    advanced_retrieval_enabled: bool = False
    code_copilot_enabled: bool = False
    operator_intelligence_enabled: bool = False
    model_orchestration_enabled: bool = False
    autonomy_reliability_enabled: bool = False

    # Autonomous engineering workspace (Prompt 39)
    engineering_memory_enabled: bool = False
    autonomous_debugging_enabled: bool = False
    safe_patching_enabled: bool = False
    dev_workflows_enabled: bool = False
    validation_fabric_enabled: bool = False
    repository_graph_enabled: bool = False
    engineering_agents_enabled: bool = False
    engineering_workspace_enabled: bool = False

    # Cognitive workstation (Prompt 40)
    context_fusion_enabled: bool = False
    workstation_awareness_enabled: bool = False
    continuous_cognition_enabled: bool = False
    execution_coordination_enabled: bool = False
    workflow_intelligence_enabled: bool = False
    live_copilot_enabled: bool = False
    cognitive_pipeline_enabled: bool = False
    cognitive_continuity_enabled: bool = False
    heavy_load: bool = False

    # Cognitive interface + embodied presence (Prompt 41)
    cognitive_shell_enabled: bool = False
    conversation_runtime_enabled: bool = False
    presence_enabled: bool = False
    cognitive_visualization_enabled: bool = False
    live_overlay_enabled: bool = False
    self_development_enabled: bool = False
    transparency_enabled: bool = False
    cognitive_interface_mode: str = "balanced"

    # Self-development loop (Prompt 42)
    self_evolution_enabled: bool = False
    self_improvement_memory_enabled: bool = False
    autonomous_patching_loop_enabled: bool = False
    runtime_benchmarks_enabled: bool = False
    evolution_governance_enabled: bool = False
    self_optimizing_routing_enabled: bool = False
    evolution_approval_level: str = "proposal_only"
    self_evolution_mode: str = "balanced"

    # Native cognitive desktop (Prompt 43)
    native_shell_enabled: bool = False
    immersive_ui_enabled: bool = False
    cognitive_daemon_enabled: bool = False
    live_engineering_enabled: bool = False
    conversational_os_enabled: bool = False
    reasoning_streams_enabled: bool = False
    native_desktop_mode: str = "balanced"

    # Persistent cognitive environment (Prompt 44)
    persistent_cognition_enabled: bool = False
    daily_continuity_enabled: bool = False
    workspace_presence_enabled: bool = False
    memory_threads_enabled: bool = False
    live_environment_enabled: bool = False
    cognitive_surface_enabled: bool = False

    # Cognitive desktop experience (Prompt 45)
    desktop_client_enabled: bool = False
    conversation_workspace_enabled: bool = False
    live_visualization_enabled: bool = False
    voice_desktop_enabled: bool = False
    daily_operator_experience_enabled: bool = False
    desktop_overlay_enabled: bool = False

    # Unified cognitive operating environment (Prompt 46)
    cognitive_workspace_enabled: bool = False
    live_reasoning_enabled: bool = False
    conversational_presence_enabled: bool = False
    evolution_review_enabled: bool = False
    operator_productivity_enabled: bool = False

    # Autonomous engineering workstation (Prompt 47)
    live_engineering_orchestrator_enabled: bool = False
    engineering_workflows_v2_enabled: bool = False
    self_improvement_sandbox_enabled: bool = False
    project_memory_enabled: bool = False
    engineering_society_enabled: bool = False
    continuous_engineering_enabled: bool = False

    # Persistent cognitive computer (Prompt 48)
    cognitive_kernel_enabled: bool = False
    memory_fabric_enabled: bool = False
    environment_intelligence_enabled: bool = False
    cognitive_streams_enabled: bool = False
    personal_presence_enabled: bool = False
    proactive_assistance_runtime_enabled: bool = False
    cognitive_orchestration_enabled: bool = False

    # Adaptive autonomous cognitive OS (Prompt 49)
    adaptive_runtime_enabled: bool = False
    autonomous_workspace_enabled: bool = False
    engineering_evolution_enabled: bool = False
    operator_intelligence_v2_enabled: bool = False
    cognitive_daemon_v2_enabled: bool = False
    autonomous_session_restore_enabled: bool = False
    cognitive_load_balancing_enabled: bool = False
    overnight_cognition_enabled: bool = False

    # Real autonomous cognitive OS (Prompt 50)
    native_os_enabled: bool = False
    autonomous_loop_v2_enabled: bool = False
    engineering_evolution_v2_enabled: bool = False
    memory_fabric_v2_enabled: bool = False
    operator_intelligence_v3_enabled: bool = False
    deep_focus_enabled: bool = False
    context_rehydration_enabled: bool = False
    autonomous_overnight_mode_enabled: bool = False

    # Cognitive infrastructure (Prompt 51)
    realtime_cognition_enabled: bool = False
    workspace_coordination_enabled: bool = False
    engineering_infrastructure_v3_enabled: bool = False
    memory_intelligence_enabled: bool = False
    operator_intelligence_v4_enabled: bool = False
    predictive_focus_enabled: bool = False
    reliability_forecasting_enabled: bool = False
    continuous_reasoning_enabled: bool = False

    # Unified cognitive core (Prompt 52)
    unified_cognitive_core_enabled: bool = False
    attention_engine_enabled: bool = False
    cognitive_scheduler_enabled: bool = False
    persistent_agents_enabled: bool = False
    runtime_coordination_enabled: bool = False
    cognitive_state_enabled: bool = False
    global_cognition_profile: str = "balanced"

    # Autonomous overnight cognition (Prompt 53)
    deferred_reasoning_enabled: bool = False
    continuity_forecasting_enabled: bool = False
    morning_briefing_enabled: bool = False
    cognitive_maintenance_enabled: bool = False
    idle_engineering_enabled: bool = False
    overnight_mode: str = "balanced"
    overnight_max_cycles: int = 32
    idle_reasoning_budget: str = "moderate"

    # Native autonomous desktop (Prompt 54)
    native_desktop_enabled: bool = False
    window_awareness_enabled: bool = False
    live_overlays_v2_enabled: bool = False
    workspace_sessions_enabled: bool = False
    operator_focus_enabled: bool = False
    desktop_attention_enabled: bool = False
    desktop_profile: str = "balanced"
    window_tracking_enabled: bool = True
    overlay_mode: str = "adaptive"

    # Milestone 15 — active perception
    runtime_observers_enabled: bool = False
    model_gemini: str = "gemini-2.0-flash"
    model_deepseek_r1: str = "deepseek-r1"
    model_deepseek_coder: str = "deepseek-coder"
    model_qwen: str = "qwen2.5"
    model_llama: str = "llama3.2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
