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
