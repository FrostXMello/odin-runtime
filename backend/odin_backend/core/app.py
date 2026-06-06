"""ODIN application container — wires all subsystems."""

import asyncio
from functools import lru_cache
from typing import Any

from odin_backend.agents.registry import AgentRegistry
from odin_backend.agents.specialized import create_specialized_agents
from odin_backend.browser.service import BrowserIntelligenceService
from odin_backend.cognition.stream import CognitionStream
from odin_backend.config import Settings, get_settings
from odin_backend.environment_control import get_environment_config
from odin_backend.core.execution_gate.gate import ExecutionGate
from odin_backend.core.execution.engine import ExecutionEngine
from odin_backend.core.runtime import AdaptiveRuntimeCoordinator, MissionExecutionBridge
from odin_backend.core.runtime.async_runtime import AsyncMissionRuntimeCoordinator
from odin_backend.core.runtime.reconciliation import ExecutionReconciliationService
from odin_backend.agents.valkyrie.engine import ValkyrieExecutionEngine
from odin_backend.cognitive_stream.aggregator import UnifiedCognitiveStream
from odin_backend.collaboration.protocol import CollaborationOrchestrator
from odin_backend.context.service import ActiveContextService
from odin_backend.context_engine.engine import ContextEngine
from odin_backend.conversation.manager import ConversationManager
from odin_backend.desktop_semantics.service import DesktopSemanticsService
from odin_backend.execution_intelligence.service import ExecutionIntelligenceService
from odin_backend.agent_society.registry import AgentSocietyRegistry
from odin_backend.compute.orchestrator import AIComputeOrchestrator
from odin_backend.desktop_runtime.manager import DesktopRuntimeManager
from odin_backend.live_cognition.engine import LiveCognitionEngine
from odin_backend.local_models.manager import LocalModelManager
from odin_backend.memory.evolution.engine import MemoryEvolutionEngine
from odin_backend.personalization.evolution import PreferenceEvolutionEngine
from odin_backend.resilience.manager import ResilienceManager
from odin_backend.security.trust import RuntimeTrustSystem
from odin_backend.workspace_automation.generator import ContextualActionGenerator
from odin_backend.workspace_intelligence.engine import WorkspaceIntelligenceEngine
from odin_backend.memory.consolidation.engine import MemoryConsolidationEngine
from odin_backend.policies.engine import PolicyEngine
from odin_backend.proactive.engine import ProactiveAssistanceEngine
from odin_backend.knowledge_graph.service import KnowledgeGraphService
from odin_backend.personalization.engine import PersonalizationEngine
from odin_backend.reflection.engine import ReflectionEngine
from odin_backend.sandbox.executor import SandboxExecutor
from odin_backend.vision.service import VisionService
from odin_backend.voice.streaming.pipeline import StreamingVoicePipeline
from odin_backend.workflows.persistent import PersistentWorkflowEngine
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.core.context_graph.graph import GlobalContextGraph
from odin_backend.core.autonomy.layer import AutonomyLayer, AutonomyLevel
from odin_backend.core.coherence.engine import CoherenceEngine
from odin_backend.core.governor.governor import ExecutionGovernor
from odin_backend.core.snapshot.engine import SnapshotEngine
from odin_backend.core.stability.loop import StabilityLoop
from odin_backend.core.missions import (
    MissionGovernance,
    MissionManager,
    MissionPlanner,
    MissionRuntime,
    MissionStateStore,
)
from odin_backend.core.checkpoints import MissionCheckpointEngine
from odin_backend.memory.missions import MissionMemoryIndex
from odin_backend.runtime.missions import MissionWorkerPool
from odin_backend.core.missions.dispatcher import ExecutionDispatcher
from odin_backend.core.missions.gc import MissionGarbageCollector
from odin_backend.core.missions.dedup import MissionDeduplicator
from odin_backend.core.missions.policy import ExecutionPolicyEnforcer
from odin_backend.core.perception import PerceptionEngine, PerceptionMemoryBridge
from odin_backend.core.feedback import ExecutionFeedbackEngine
from odin_backend.core.confidence import ConfidenceTracker
from odin_backend.core.execution_gate.adaptive_policy import AdaptiveExecutionPolicy
from odin_backend.memory.perception import PerceptionMemoryStore
from odin_backend.runtime.observers import RuntimeObserverManager
from odin_backend.memory.refinement.engine import MemoryRefinementEngine
from odin_backend.agents.protocol import AgentProtocolHub
from odin_backend.core.conscious_loop.loop import RuntimeConsciousLoop
from odin_backend.core.execution.contract import ExecutionContract
from odin_backend.core.model_router.router import KernelModelRouter
from odin_backend.runtime.bootstrap.boot import OdinBootstrap
from odin_backend.runtime.loop.engine import LiveExecutionLoop
from odin_backend.tools.execution.pipeline import LiveToolPipeline
from odin_backend.core.kernel.kernel import OdinCognitiveKernel
from odin_backend.core.priority.engine import CognitivePriorityEngine
from odin_backend.events.bus import EventBus, InMemoryEventBus
from odin_backend.events.redis_bus import RedisEventBus
from odin_backend.events.redis_client import RedisClient
from odin_backend.events.task_queue import TaskQueue
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.monitoring.audit import AuditLogger
from odin_backend.monitoring.event_hub import EventHub
from odin_backend.monitoring.logging import configure_logging, get_logger
from odin_backend.monitoring.metrics import MetricsCollector
from odin_backend.monitoring.tracing import TraceManager
from odin_backend.core.observability import ObservabilityHub
from odin_backend.core.streaming import WebSocketManager, set_stream_bridge
from odin_backend.core.streaming.heartbeat import StreamHeartbeat
from odin_backend.orchestrator.odin import OdinOrchestrator
from odin_backend.orchestrator.reasoning.reasoning_engine import ReasoningEngine
from odin_backend.permissions.heimdall import HeimdallService
from odin_backend.permissions.service import PermissionService
from odin_backend.runtime.supervisor.supervisor import RuntimeSupervisor
from odin_backend.tools.implementations.registry_setup import register_all_tools
from odin_backend.tools.registry import ToolRegistry
from odin_backend.tools.runtime.executor import RuntimeToolExecutor
from odin_backend.voice.sessions import VoiceSessionManager
from odin_backend.watchers.manager import WatcherManager
from odin_backend.workflows.dag_runner import DAGWorkflowRunner

logger = get_logger(__name__)


class OdinApplication:
    """Central dependency container for ODIN backend."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        use_redis: bool = True,
        env_config: Any = None,
    ) -> None:
        self.settings = settings or get_settings()
        if env_config is not None:
            self.env_config = env_config
        else:
            self.env_config = get_environment_config()
            if settings is not None:
                self.env_config = self.env_config.model_copy(
                    update={"autonomy_level": settings.default_autonomy_level}
                )
        self.use_redis = use_redis

        self.event_bus: EventBus
        self.redis_client: RedisClient | None = None
        self.event_hub = EventHub()
        self.trace_manager = TraceManager()
        self.audit_logger = AuditLogger()
        self.metrics = MetricsCollector()
        self.observability = ObservabilityHub(self.metrics)
        self.stream_bus = self.observability.stream_bus
        self.stream_ws = WebSocketManager(self.stream_bus)
        self.stream_heartbeat = StreamHeartbeat(
            self.stream_bus,
            interval_seconds=self.settings.streaming_heartbeat_interval_seconds,
        )

        self.permission_service = PermissionService()
        self.tool_registry = ToolRegistry(self.permission_service)
        self.heimdall: HeimdallService
        self.tool_executor: RuntimeToolExecutor
        self.memory: MimirCoordinator
        self.reasoning: ReasoningEngine
        self.workflow_runner: DAGWorkflowRunner
        self.task_queue: TaskQueue
        self.agent_registry = AgentRegistry()
        self.orchestrator: OdinOrchestrator
        self.runtime: RuntimeSupervisor
        self.browser: BrowserIntelligenceService
        self.context: ActiveContextService
        self.voice: VoiceSessionManager
        self.watchers: WatcherManager
        self.conversation: ConversationManager
        self.knowledge_graph: KnowledgeGraphService
        self.sandbox: SandboxExecutor
        self.vision: VisionService
        self.personalization: PersonalizationEngine
        self.reflection: ReflectionEngine
        self.persistent_workflows: PersistentWorkflowEngine
        self.voice_stream: StreamingVoicePipeline
        self.context_engine: ContextEngine
        self.desktop_semantics: DesktopSemanticsService
        self.execution_intelligence: ExecutionIntelligenceService
        self.collaboration: CollaborationOrchestrator
        self.unified_cognition: UnifiedCognitiveStream
        self.memory_consolidation: MemoryConsolidationEngine
        self.proactive: ProactiveAssistanceEngine
        self.local_models: LocalModelManager
        self.policy_engine: PolicyEngine
        self.desktop_runtime: DesktopRuntimeManager
        self.workspace_intelligence: WorkspaceIntelligenceEngine
        self.live_cognition: LiveCognitionEngine
        self.resilience: ResilienceManager
        self.agent_society: AgentSocietyRegistry
        self.preference_evolution: PreferenceEvolutionEngine
        self.memory_evolution: MemoryEvolutionEngine
        self.compute: AIComputeOrchestrator
        self.trust_system: RuntimeTrustSystem
        self.workspace_automation: ContextualActionGenerator
        self.kernel: OdinCognitiveKernel
        self.context_graph: GlobalContextGraph
        self.priority_engine: CognitivePriorityEngine
        self.governor: ExecutionGovernor
        self.coherence: CoherenceEngine
        self.autonomy: AutonomyLayer
        self.snapshots: SnapshotEngine
        self.stability: StabilityLoop
        self.memory_refinement: MemoryRefinementEngine
        self.agent_protocol: AgentProtocolHub
        self.execution_contract: ExecutionContract
        self.execution_engine: ExecutionEngine
        self.mission_execution_bridge: MissionExecutionBridge
        self.mission_execution_adaptive: AdaptiveRuntimeCoordinator
        self.async_mission_runtime: AsyncMissionRuntimeCoordinator
        self.execution_reconciliation: ExecutionReconciliationService
        self.conscious_loop: RuntimeConsciousLoop
        self.live_loop: LiveExecutionLoop
        self.model_router: KernelModelRouter
        self.live_tools: LiveToolPipeline
        self.bootstrap: OdinBootstrap
        self.env_config: Any
        self.execution_gate: ExecutionGate
        self.valkyrie: ValkyrieExecutionEngine
        self._inner_bus: EventBus

        self._build()

    def _build(self) -> None:
        if self.use_redis:
            self._inner_bus = RedisEventBus(self.settings)
            self.redis_client = RedisClient(self.settings)
        else:
            self._inner_bus = InMemoryEventBus()
            self.redis_client = None

        self.event_bus = SignalUnificationBus(self._inner_bus)
        self.context_graph = GlobalContextGraph()
        self.priority_engine = CognitivePriorityEngine(self.context_graph)
        self.coherence = CoherenceEngine(
            self.context_graph,
            self.priority_engine,
            execution_threshold=self.settings.coherence_execution_threshold,
        )
        self.autonomy = AutonomyLayer(
            AutonomyLevel(self.env_config.autonomy_level)
        )
        self.snapshots = SnapshotEngine()
        self.stability = StabilityLoop(self.event_bus)

        self.cognition = CognitionStream(self.event_bus)

        self.heimdall = HeimdallService(
            self.permission_service, self.event_bus, self.audit_logger
        )
        self.policy_engine = PolicyEngine(self.settings, self.event_bus, self.heimdall)
        self.tool_executor = RuntimeToolExecutor(
            self.tool_registry,
            self.event_bus,
            self.heimdall,
            self.trace_manager,
            self.audit_logger,
        )
        self.tool_executor.set_policy_engine(self.policy_engine)
        self.sandbox = SandboxExecutor(self.settings, self.event_bus, self.tool_executor)
        self.memory = MimirCoordinator(
            self.event_bus, self.settings, observability=self.observability
        )
        self.conversation = ConversationManager(self.settings, self.event_bus, self.memory)
        self.knowledge_graph = KnowledgeGraphService(self.event_bus)
        self.personalization = PersonalizationEngine(self.memory)
        self.preference_evolution = PreferenceEvolutionEngine(self.personalization)
        self.memory_evolution = MemoryEvolutionEngine(self.memory, self.event_bus)
        self.reflection = ReflectionEngine(self.event_bus)
        self.persistent_workflows = PersistentWorkflowEngine(self.settings, self.event_bus)
        self.vision = VisionService(self.event_bus)
        self.reasoning = ReasoningEngine(self.settings, self.event_bus, self.cognition)
        self.browser = BrowserIntelligenceService(self.settings, self.event_bus)
        self.context = ActiveContextService(self.settings, self.event_bus)
        self.context_engine = ContextEngine(self.settings, self.event_bus)
        self.desktop_runtime = DesktopRuntimeManager(
            self.settings, self.event_bus, self.context_engine
        )
        self.workspace_intelligence = WorkspaceIntelligenceEngine(self.event_bus)
        self.desktop_semantics = DesktopSemanticsService(self.event_bus)
        self.resilience = ResilienceManager(self.event_bus)
        self.workspace_automation = ContextualActionGenerator()
        self.execution_intelligence_service = ExecutionIntelligenceService(self.event_bus)
        self.unified_cognition = UnifiedCognitiveStream(self.event_bus, self.cognition)
        self.live_cognition = LiveCognitionEngine(
            self.event_bus,
            self.unified_cognition,
            self.context_engine,
            self.workspace_intelligence,
        )
        self.memory_consolidation = MemoryConsolidationEngine(self.memory, self.event_bus)
        self.local_models = LocalModelManager(self.settings, self.event_bus)
        self.voice = VoiceSessionManager(self.settings, self.event_bus)
        self.voice_stream = StreamingVoicePipeline(self.voice, self.cognition, self.event_bus)
        self.watchers = WatcherManager(self.settings, self.event_bus, self.audit_logger)
        self.runtime = RuntimeSupervisor(self.settings, self.event_bus, self.agent_registry)

        redis_for_queue = self.redis_client or RedisClient(self.settings)
        self.task_queue = TaskQueue(redis_for_queue, self.event_bus)
        self.orchestrator = OdinOrchestrator(
            self.settings,
            self.event_bus,
            self.task_queue,
            self.agent_registry,
        )

        register_all_tools(self.tool_registry)
        for agent in create_specialized_agents(
            self.event_bus, self.tool_executor, self.memory
        ):
            self.agent_registry.register(agent)

        self.workflow_runner = DAGWorkflowRunner(
            self.event_bus,
            self.agent_registry,
            self.memory,
            self.trace_manager,
            self.cognition,
            self.metrics,
            max_parallel=self.settings.workflow_max_parallel_steps,
        )
        self.collaboration = CollaborationOrchestrator(self.event_bus, self.agent_registry)
        self.agent_society_registry = AgentSocietyRegistry(self.agent_registry)
        self.compute = AIComputeOrchestrator(
            self.settings,
            self.event_bus,
            self.local_models,
            self.reasoning._router,  # noqa: SLF001
        )
        self.trust_system = RuntimeTrustSystem(self.event_bus, self.policy_engine)
        self.governor = ExecutionGovernor(
            self.event_bus,
            self.policy_engine,
            self.trust_system,
            self.context_graph,
        )
        self.memory_refinement = MemoryRefinementEngine(self.memory, self.event_bus)
        self.kernel = OdinCognitiveKernel(
            self.event_bus,
            self.context_graph,
            self.priority_engine,
            self.governor,
            coherence=self.coherence,
        )
        self.kernel.set_environment_config(self.env_config)
        self.kernel.set_runtime_providers(
            autonomy=self.autonomy,
            agent_registry=self.agent_registry,
            memory=self.memory,
        )
        self._apply_env_to_settings()
        self.agent_protocol = AgentProtocolHub(self.event_bus, self.kernel)
        self.execution_contract = ExecutionContract()
        self._sqlite_execution_store = None
        self.execution_engine = ExecutionEngine(self)
        if self.settings.execution_persist_enabled:
            from odin_backend.core.execution.persistence import PersistedExecutionStore, SqliteExecutionStore

            self._sqlite_execution_store = SqliteExecutionStore(self.settings)
            self.execution_engine.store = PersistedExecutionStore(self._sqlite_execution_store)
        self.mission_execution_adaptive = AdaptiveRuntimeCoordinator()
        self.mission_execution_bridge = MissionExecutionBridge(self)
        self.async_mission_runtime = AsyncMissionRuntimeCoordinator(self)
        self.execution_reconciliation = ExecutionReconciliationService(self)
        self.model_router = KernelModelRouter(self.settings)
        self.live_loop = LiveExecutionLoop(self)
        self.live_tools = LiveToolPipeline()
        self.execution_gate = ExecutionGate()
        self.adaptive_policy = AdaptiveExecutionPolicy(self.execution_gate)
        self.perception_memory = PerceptionMemoryStore(self.memory)
        self.perception_bridge = PerceptionMemoryBridge(
            self.perception_memory, self.context_graph
        )
        self.perception = PerceptionEngine(self.event_bus, self.perception_bridge)
        self.feedback = ExecutionFeedbackEngine()
        self.confidence = ConfidenceTracker()
        self.valkyrie = ValkyrieExecutionEngine(self)
        self.bootstrap = OdinBootstrap()
        self.mission_store = MissionStateStore(self.memory.structured)
        self.mission_memory = MissionMemoryIndex(self.memory)
        self.mission_planner = MissionPlanner()
        self.mission_governance = MissionGovernance()
        self.mission_checkpoints = MissionCheckpointEngine(self.mission_store)
        self.mission_policy = ExecutionPolicyEnforcer()
        self.mission_deduplicator = MissionDeduplicator(
            replay_window_seconds=self.settings.mission_replay_window_seconds
        )
        self.mission_manager = MissionManager(
            self.mission_store,
            self.mission_planner,
            memory_index=self.mission_memory,
            deduplicator=self.mission_deduplicator,
            policy=self.mission_policy,
            replay_window_seconds=self.settings.mission_replay_window_seconds,
            observability=self.observability,
        )
        self.mission_runtime = MissionRuntime(
            self.mission_planner,
            self.mission_governance,
            self.mission_checkpoints,
            self.mission_memory,
            feedback=self.feedback,
            confidence=self.confidence,
            policy=self.mission_policy,
        )
        self.mission_worker = MissionWorkerPool(self)
        self.mission_dispatcher = ExecutionDispatcher(self)
        from odin_backend.core.queueing.service import DistributedQueueService
        from odin_backend.core.queueing.recovery import DistributedRecoveryCoordinator
        from odin_backend.core.runtime.workers import WorkerRegistry

        self.distributed_queue = DistributedQueueService(self)
        self.distributed_recovery = DistributedRecoveryCoordinator(self)
        self.worker_registry = WorkerRegistry(self.settings, self.distributed_queue.worker_id)
        from odin_backend.core.distributed.routing import CapabilityRouter
        from odin_backend.core.distributed.topology import RuntimeTopology
        from odin_backend.core.distributed.pubsub import DistributedPubSub
        from odin_backend.core.execution.pools.pool_manager import ExecutionPoolManager

        self.capability_router = CapabilityRouter(self)
        self.runtime_topology = RuntimeTopology(self)
        self.distributed_pubsub = DistributedPubSub(self.settings)
        self.execution_pool_manager = ExecutionPoolManager(self)
        from odin_backend.core.memory.context import MissionContextService
        from odin_backend.core.tools.registry import IntelligentToolRegistry
        from odin_backend.core.tools.selector import ToolSelector
        from odin_backend.core.tools.tool_memory import ToolMemory
        from odin_backend.core.planning.validators import PlanValidator

        self.mission_context = MissionContextService(self)
        self.intelligent_tool_registry = IntelligentToolRegistry(self)
        self.intelligent_tool_registry.sync_from_legacy()
        self.tool_selector = ToolSelector(self.intelligent_tool_registry)
        self.tool_memory = ToolMemory(self.settings)
        self.plan_validator = PlanValidator()
        self.mission_planner._app = self
        self.mission_planner._semantic._app = self
        from odin_backend.core.cognition import CognitiveMemoryGraph, RetrievalEngine
        from odin_backend.core.cognition.experience import ExperienceEngine
        from odin_backend.core.cognition.failures import FailureIntelligence
        from odin_backend.core.cognition.improvement import ImprovementLoop
        from odin_backend.core.cognition.improvement.learning_scheduler import LearningScheduler
        from odin_backend.core.execution.intelligence import ExecutionIntelligence

        self.cognitive_memory = CognitiveMemoryGraph(self.settings, self)
        self.memory_retrieval = RetrievalEngine(self.cognitive_memory)
        self.experience_engine = ExperienceEngine(self)
        self.execution_intelligence = ExecutionIntelligence(
            self, legacy_service=self.execution_intelligence_service
        )
        self.failure_intelligence = FailureIntelligence(self)
        self.improvement_loop = ImprovementLoop(self)
        self._learning_scheduler = LearningScheduler(self, interval_seconds=300.0)
        from odin_backend.core.models.registry import LocalModelRegistry
        from odin_backend.core.models.model_manager import ModelManager
        from odin_backend.core.cognition.reasoning import ReasoningPipeline
        from odin_backend.core.cognition.reflection import ReflectionEngine as CognitiveReflectionEngine
        from odin_backend.core.embeddings import EmbeddingRuntime
        from odin_backend.core.resources import ModelResourceScheduler
        from odin_backend.core.agents import CognitiveAgentCoordinator

        self.model_registry = LocalModelRegistry(self.settings)
        self.model_manager = ModelManager(self.settings, self.model_registry, self)
        self.reasoning_pipeline = ReasoningPipeline(self)
        self.cognitive_reflection = CognitiveReflectionEngine(self)
        self.embedding_runtime = EmbeddingRuntime(self)
        self.model_resource_scheduler = ModelResourceScheduler(self)
        self.cognitive_agents = CognitiveAgentCoordinator(self)
        from odin_backend.core.autonomy.autonomy_loop import AutonomousLoopEngine
        from odin_backend.core.autonomy.objective_manager import ObjectiveManager
        from odin_backend.core.environment.environment_monitor import EnvironmentMonitor
        from odin_backend.core.research.research_engine import ResearchEngine
        from odin_backend.core.identity.identity_store import IdentityStore
        from odin_backend.core.safety.autonomy_policy_engine import AutonomyPolicyEngine

        self.objective_manager = ObjectiveManager(self)
        self.autonomy_safety = AutonomyPolicyEngine(self)
        self.autonomous_loop = AutonomousLoopEngine(self)
        self.environment_monitor = EnvironmentMonitor(self)
        self.research_engine = ResearchEngine(self)
        self.identity_store = IdentityStore(self.settings)
        if getattr(self.settings, "autonomy_mode", "supervised"):
            self.autonomous_loop.set_mode(self.settings.autonomy_mode)
        from odin_backend.core.perception.perception_runtime import MultimodalPerceptionRuntime
        from odin_backend.core.desktop.desktop_monitor import DesktopMonitor
        from odin_backend.core.vision.screen_pipeline import ScreenUnderstandingPipeline
        from odin_backend.core.voice import VoiceRuntime
        from odin_backend.core.copilot import CopilotRuntime
        from odin_backend.core.copilot.workspace_memory import WorkspaceMemoryStore
        from odin_backend.core.collaboration import CollaborationRuntime

        self.multimodal_perception = MultimodalPerceptionRuntime(self)
        self.desktop_monitor = DesktopMonitor(self)
        self.screen_pipeline = ScreenUnderstandingPipeline(self)
        self.voice_runtime = VoiceRuntime(self)
        self.copilot_runtime = CopilotRuntime(self)
        self.workspace_memory = WorkspaceMemoryStore(self.settings)
        self.collaboration_runtime = CollaborationRuntime(self)
        from odin_backend.core.actions import ActionRuntime
        from odin_backend.core.actions.action_scheduler import ActionScheduler
        from odin_backend.core.automation import AutomationSandbox
        from odin_backend.core.browser_operator import BrowserOperatorRuntime
        from odin_backend.core.supervision import SupervisionRuntime
        from odin_backend.core.workflow_macros import MacroReplayEngine
        from odin_backend.core.workflow_macros.workflow_memory import WorkflowMemoryStore
        from odin_backend.core.action_safety import ActionSafetyEngine
        from odin_backend.core.overlay import OverlayRuntime

        self.action_safety = ActionSafetyEngine(self)
        self.action_runtime = ActionRuntime(self)
        self.action_scheduler = ActionScheduler(self)
        self.automation_sandbox = AutomationSandbox(self)
        self.browser_operator = BrowserOperatorRuntime(self)
        self.supervision_runtime = SupervisionRuntime(self)
        self.workflow_memory = WorkflowMemoryStore(self.settings)
        self.macro_replay = MacroReplayEngine(self)
        self.overlay_runtime = OverlayRuntime(self)
        from odin_backend.core.knowledge import KnowledgeRuntime
        from odin_backend.core.knowledge.research_governance import ResearchGovernance
        from odin_backend.core.research_engine import ResearchFabricRuntime
        from odin_backend.core.web_access import WebAccessRuntime
        from odin_backend.core.research_agents import ResearchSwarmCoordinator
        from odin_backend.core.reasoning import WorldReasoner

        self.knowledge_runtime = KnowledgeRuntime(self)
        self.research_governance = ResearchGovernance(self)
        self.research_fabric = ResearchFabricRuntime(self)
        self.web_access = WebAccessRuntime(self)
        self.research_agents = ResearchSwarmCoordinator(self)
        self.reasoning_world = WorldReasoner(self)
        from odin_backend.core.agent_society import AgentSocietyRuntime
        from odin_backend.core.agent_messages import AgentMessageBus
        from odin_backend.core.learning_society import PeerLearningEngine

        self.agent_society = AgentSocietyRuntime(self, legacy_registry=self.agent_society_registry)
        self.agent_messages = AgentMessageBus(self)
        self.peer_learning = PeerLearningEngine(self)
        from odin_backend.core.federation import FederationRuntime
        from odin_backend.core.federated_agents import SocietyFederation
        from odin_backend.core.world_simulation import WorldSimulationRuntime
        from odin_backend.core.strategic_reasoning import StrategicReasoningRuntime
        from odin_backend.core.federated_memory import FederatedMemoryRuntime
        from odin_backend.core.federation_governance import FederationGovernanceRuntime

        self.federation_runtime = FederationRuntime(self)
        self.society_federation = SocietyFederation(self)
        self.world_simulation = WorldSimulationRuntime(self)
        self.strategic_reasoning = StrategicReasoningRuntime(self)
        self.federated_memory = FederatedMemoryRuntime(self)
        self.federation_governance = FederationGovernanceRuntime(self)
        from odin_backend.core.runtime_continuity import ContinuityRuntime
        from odin_backend.core.background_cognition import BackgroundCognitionRuntime
        from odin_backend.core.runtime_evolution import EvolutionRuntime
        from odin_backend.core.cognitive_economy import CognitiveEconomyRuntime
        from odin_backend.core.meta_reasoning import MetaReasoningRuntime
        from odin_backend.core.operational_planning import OperationalPlanningRuntime
        from odin_backend.core.operator_relationship import OperatorRelationshipRuntime
        from odin_backend.core.distributed_optimization import DistributedOptimizationRuntime

        self.continuity_runtime = ContinuityRuntime(self)
        self.background_cognition = BackgroundCognitionRuntime(self)
        self.evolution_runtime = EvolutionRuntime(self)
        self.cognitive_economy = CognitiveEconomyRuntime(self)
        self.meta_reasoning = MetaReasoningRuntime(self)
        self.operational_planning = OperationalPlanningRuntime(self)
        self.operator_relationship = OperatorRelationshipRuntime(self)
        self.distributed_optimization = DistributedOptimizationRuntime(self)
        from odin_backend.core.local_ai import LocalAIRuntime
        from odin_backend.core.vector_memory import VectorMemoryRuntime
        from odin_backend.core.agent_execution import AgentExecutionRuntime
        from odin_backend.core.copilot.copilot_production_runtime import CopilotProductionRuntime
        from odin_backend.core.realtime_voice import RealtimeVoiceRuntime
        from odin_backend.core.evaluation import BenchmarkRuntime
        from odin_backend.core.resource_optimization import ResourceOptimizationRuntime
        from odin_backend.core.daemon import DaemonRuntime

        self.local_ai = LocalAIRuntime(self)
        self.vector_memory = VectorMemoryRuntime(self)
        self.agent_execution = AgentExecutionRuntime(self)
        self.copilot_production = CopilotProductionRuntime(self)
        self.realtime_voice = RealtimeVoiceRuntime(self)
        self.benchmark_runtime = BenchmarkRuntime(self)
        self.resource_optimization = ResourceOptimizationRuntime(self)
        self.daemon_runtime = DaemonRuntime(self)
        from odin_backend.core.stability import RuntimeGuardian
        from odin_backend.core.self_healing import SelfHealingRuntime
        from odin_backend.core.automation.automation_runtime import AutomationRuntime

        self.runtime_guardian = RuntimeGuardian(self)
        self.self_healing = SelfHealingRuntime(self)
        self.automation_runtime = AutomationRuntime(self)
        from odin_backend.core.project_os import ProjectOSRuntime
        from odin_backend.core.integrations import IntegrationsRuntime
        from odin_backend.core.workspace_knowledge import WorkspaceKnowledgeRuntime
        from odin_backend.core.productivity import ProductivityRuntime
        from odin_backend.core.communications import CommunicationsRuntime
        from odin_backend.core.storage_optimization import StorageOptimizationRuntime

        self.project_os = ProjectOSRuntime(self)
        self.integrations_runtime = IntegrationsRuntime(self)
        self.workspace_knowledge = WorkspaceKnowledgeRuntime(self)
        self.productivity_runtime = ProductivityRuntime(self)
        self.communications_runtime = CommunicationsRuntime(self)
        self.storage_optimization = StorageOptimizationRuntime(self)
        from odin_backend.deployment import DeploymentRuntime
        from odin_backend.core.performance import PerformanceRuntime
        from odin_backend.core.privacy import PrivacyRuntime
        from odin_backend.core.operator_shell import OperatorShellRuntime
        from odin_backend.core.daily_workflow.daily_workflow_runtime import DailyWorkflowRuntime

        self.deployment = DeploymentRuntime(self)
        self.performance = PerformanceRuntime(self)
        self.privacy = PrivacyRuntime(self)
        self.operator_shell = OperatorShellRuntime(self)
        self.daily_workflow = DailyWorkflowRuntime(self)
        from odin_backend.core.intelligence_quality import IntelligenceQualityRuntime
        from odin_backend.core.copilot.code_copilot_runtime import CodeCopilotRuntime
        from odin_backend.core.operator_relationship.operator_intelligence_runtime import OperatorIntelligenceRuntime
        from odin_backend.core.local_ai.model_orchestration_runtime import ModelOrchestrationRuntime
        from odin_backend.core.autonomy.autonomy_reliability_runtime import AutonomyReliabilityRuntime

        self.intelligence_quality = IntelligenceQualityRuntime(self)
        self.code_copilot = CodeCopilotRuntime(self)
        self.operator_intelligence = OperatorIntelligenceRuntime(self)
        self.model_orchestration = ModelOrchestrationRuntime(self)
        self.autonomy_reliability = AutonomyReliabilityRuntime(self)
        from odin_backend.core.engineering_memory import EngineeringMemoryRuntime
        from odin_backend.core.autonomous_debugging import AutonomousDebuggingRuntime
        from odin_backend.core.patching import PatchingRuntime
        from odin_backend.core.dev_workflows import DevWorkflowsRuntime
        from odin_backend.core.validation_fabric import ValidationFabricRuntime
        from odin_backend.core.copilot.repository_graph_runtime import RepositoryGraphRuntime
        from odin_backend.core.agent_society.engineering_agents_runtime import EngineeringAgentsRuntime

        self.engineering_memory = EngineeringMemoryRuntime(self)
        self.autonomous_debugging = AutonomousDebuggingRuntime(self)
        self.patching = PatchingRuntime(self)
        self.dev_workflows = DevWorkflowsRuntime(self)
        self.validation_fabric = ValidationFabricRuntime(self)
        self.repository_graph = RepositoryGraphRuntime(self)
        self.engineering_agents = EngineeringAgentsRuntime(self)
        from odin_backend.core.context_fusion import ContextFusionRuntime
        from odin_backend.core.workstation import WorkstationAwarenessRuntime
        from odin_backend.core.continuous_cognition import ContinuousCognitionRuntime
        from odin_backend.core.execution_coordination import ExecutionCoordinationRuntime
        from odin_backend.core.workflow_intelligence import WorkflowIntelligenceRuntime
        from odin_backend.core.copilot.live_assistance_runtime import LiveCopilotRuntime
        from odin_backend.core.cognitive_continuity import CognitiveContinuityRuntime
        from odin_backend.core.local_ai.cognitive_pipeline_runtime import CognitivePipelineRuntime

        self.context_fusion = ContextFusionRuntime(self)
        self.workstation_awareness = WorkstationAwarenessRuntime(self)
        self.continuous_cognition = ContinuousCognitionRuntime(self)
        self.execution_coordination = ExecutionCoordinationRuntime(self)
        self.workflow_intelligence = WorkflowIntelligenceRuntime(self)
        self.live_copilot = LiveCopilotRuntime(self)
        self.cognitive_continuity = CognitiveContinuityRuntime(self)
        self.cognitive_pipeline = CognitivePipelineRuntime(self)
        from odin_backend.core.cognitive_shell import CognitiveShellRuntime
        from odin_backend.core.conversation_runtime import ConversationRuntime
        from odin_backend.core.presence import PresenceRuntime
        from odin_backend.core.cognitive_visualization import CognitiveVisualizationRuntime
        from odin_backend.core.live_overlay import LiveOverlayRuntime
        from odin_backend.core.self_development import SelfDevelopmentRuntime
        from odin_backend.core.transparency import TransparencyRuntime

        self.cognitive_shell = CognitiveShellRuntime(self)
        self.conversation = ConversationRuntime(self)
        self.presence = PresenceRuntime(self)
        self.cognitive_visualization = CognitiveVisualizationRuntime(self)
        self.live_overlay = LiveOverlayRuntime(self)
        self.self_development = SelfDevelopmentRuntime(self)
        self.transparency = TransparencyRuntime(self)
        from odin_backend.core.self_evolution import SelfEvolutionRuntime
        from odin_backend.core.self_improvement_memory import SelfImprovementMemoryRuntime
        from odin_backend.core.autonomous_patching import AutonomousPatchingRuntime
        from odin_backend.core.runtime_benchmarks import RuntimeBenchmarksRuntime
        from odin_backend.core.evolution_governance import EvolutionGovernanceRuntime

        self.self_evolution = SelfEvolutionRuntime(self)
        self.self_improvement_memory = SelfImprovementMemoryRuntime(self)
        self.autonomous_patching = AutonomousPatchingRuntime(self)
        self.runtime_benchmarks = RuntimeBenchmarksRuntime(self)
        self.evolution_governance = EvolutionGovernanceRuntime(self)
        from odin_backend.core.native_shell import NativeShellRuntime
        from odin_backend.core.immersive_ui import ImmersiveUiRuntime
        from odin_backend.core.live_engineering import LiveEngineeringRuntime
        from odin_backend.core.conversational_os import ConversationalOSRuntime
        from odin_backend.core.reasoning_streams import ReasoningStreamsRuntime

        self.native_shell = NativeShellRuntime(self)
        self.immersive_ui = ImmersiveUiRuntime(self)
        self.live_engineering = LiveEngineeringRuntime(self)
        self.conversational_os = ConversationalOSRuntime(self)
        self.reasoning_streams = ReasoningStreamsRuntime(self)
        self.mission_gc = MissionGarbageCollector(
            self.mission_store,
            stale_seconds=self.settings.mission_gc_stale_seconds,
        )
        self._mission_gc_task: asyncio.Task | None = None
        self.runtime_observers = RuntimeObserverManager(self)
        self.kernel.set_mission_providers(
            manager=self.mission_manager,
            runtime=self.mission_runtime,
        )
        self.kernel.set_perception_providers(
            perception=self.perception,
            confidence=self.confidence,
            perception_memory=self.perception_memory,
        )
        self.conscious_loop = RuntimeConsciousLoop(self)
        self.reasoning.set_kernel(self.kernel)
        self.orchestrator.set_agent_protocol(self.agent_protocol)
        self.governor.set_kernel(self.kernel)
        self.governor.set_autonomy(self.autonomy)
        self.governor.set_coherence(self.coherence)
        if isinstance(self.event_bus, SignalUnificationBus):
            self.event_bus.set_kernel(self.kernel)
            self.event_bus.set_kernel_enabled(self.env_config.kernel_enabled)
            self.event_bus.set_observability(self.observability)
        self.tool_executor.set_governor(self.governor)
        self.proactive = ProactiveAssistanceEngine(
            self.event_bus,
            self.context_engine,
            self.desktop_semantics,
            self.execution_intelligence,
        )

        self.runtime.register_service("watchers", self.watchers)
        self.runtime.register_service("browser", self.browser)

    def _apply_env_to_settings(self) -> None:
        """Bridge environment config into legacy settings (no hardcoded runtime flags)."""
        ec = self.env_config
        self.settings.live_loop_enabled = ec.live_loop_enabled
        self.settings.live_loop_interval_seconds = ec.live_loop_interval_seconds
        self.settings.conscious_loop_enabled = ec.conscious_loop_enabled
        self.settings.stability_loop_enabled = ec.stability_loop_enabled
        self.settings.default_autonomy_level = ec.autonomy_level
        self.settings.ollama_base_url = ec.ollama_url
        self.settings.model_base_url = ec.ollama_url
        if ec.gemini_api_key and not self.settings.openai_api_key:
            self.settings.openai_api_key = ec.gemini_api_key
        if ec.openai_api_key:
            self.settings.openai_api_key = ec.openai_api_key
        primary_map = {
            "gemini": self.settings.model_gemini,
            "deepseek-r1": self.settings.model_deepseek_r1,
            "deepseek-coder": self.settings.model_deepseek_coder,
        }
        self.settings.model_gemini = primary_map.get(ec.model_primary, ec.model_primary)

    async def _bridge_events(self, event) -> None:
        await self.event_hub.publish(event)
        try:
            await self.unified_cognition.subscribe_event(event)
        except Exception:
            pass

    async def startup(self) -> None:
        configure_logging(self.settings)
        if self.use_redis:
            try:
                await self.redis_client.connect()  # type: ignore[union-attr]
                await self.event_bus.connect()  # type: ignore[attr-defined]
            except Exception as exc:
                logger.warning("redis_unavailable_fallback", error=str(exc))
                self.use_redis = False
                self._inner_bus = InMemoryEventBus()
                self.event_bus = SignalUnificationBus(self._inner_bus)
                self.event_bus.set_kernel(self.kernel)
                await self.event_bus.connect()
        else:
            await self.event_bus.connect()

        await self.memory.startup()
        await self.mission_manager.connect()
        await self.distributed_queue.connect()
        await self.distributed_pubsub.connect()
        await self.mission_context.connect()
        await self.tool_memory.connect()
        await self.cognitive_memory.connect()
        if getattr(self.settings, "local_cognition_enabled", True):
            await self.model_manager.connect()
            await self.embedding_runtime.connect()
        await self.objective_manager.connect()
        await self.identity_store.connect()
        await self.workspace_memory.connect()
        await self.workflow_memory.connect()
        await self.knowledge_runtime.connect()
        await self.agent_society.connect()
        await self.federation_runtime.connect()
        await self.world_simulation.connect()
        await self.federated_memory.connect()
        await self.continuity_runtime.connect()
        await self.operator_relationship.connect()
        await self.local_ai.connect()
        await self.vector_memory.connect()
        await self.agent_execution.connect()
        await self.runtime_guardian.connect()
        await self.project_os.connect()
        if getattr(self.settings, "deployment_enabled", False):
            await self.deployment.validate()
        if getattr(self.settings, "action_engine_enabled", False):
            await self.action_scheduler.start()
        if getattr(self.settings, "autonomous_operator_enabled", False):
            await self.autonomous_loop.start()
        if getattr(self.settings, "cognitive_learning_enabled", True):
            await self._learning_scheduler.start()
        if self._sqlite_execution_store:
            await self._sqlite_execution_store.connect()
        await self.worker_registry.connect()
        if self.settings.distributed_recovery_enabled:
            await self.distributed_recovery.recover_on_startup()
        elif self.settings.async_mission_runtime_enabled:
            await self.execution_reconciliation.reconcile_on_startup()
        if self.settings.mission_gc_enabled:
            await self.mission_gc.run(self.mission_manager)
        if self.settings.mission_restore_on_startup:
            restored = await self.mission_manager.restore_active(
                max_restore=self.settings.mission_restore_max,
            )
            for m in restored:
                self.mission_worker.enqueue_mission(m.mission_id)
        await self.context_engine.startup()
        if self.settings.local_model_warm_on_startup:
            await self.local_models.warm_model()
        await self.personalization.load()
        await self.preference_evolution.load()
        await self.event_bus.subscribe_all(self._bridge_events)
        await self.agent_registry.register_all()
        await self.orchestrator.start()
        await self.runtime.start()
        if self.settings.runtime_enable_background_loops:
            await self.watchers.start_all()
        await self.bootstrap.boot(self)
        await self.mission_worker.start()
        if self.settings.mission_dispatch_enabled:
            await self.mission_dispatcher.start()
        if self.settings.streaming_enabled:
            set_stream_bridge(self.observability.stream_bridge)
            await self.stream_heartbeat.start(self)
        if self.settings.execution_engine_enabled:
            await self.execution_engine.start()
        if (
            self.settings.async_mission_runtime_enabled
            and not self.settings.distributed_recovery_enabled
        ):
            await self.execution_reconciliation.reconcile_on_startup()
        await self.worker_registry.start_heartbeat_loop(self)
        if self.settings.mission_gc_enabled:
            self._mission_gc_task = asyncio.create_task(self._mission_gc_loop())
        if self.settings.runtime_observers_enabled:
            await self.runtime_observers.start_all()
        if self.settings.live_loop_enabled:
            await self.live_loop.start()
        elif self.settings.conscious_loop_enabled:
            await self.conscious_loop.start()
        if (
            self.settings.stability_loop_enabled
            and not self.settings.conscious_loop_enabled
            and not self.settings.live_loop_enabled
        ):
            await self.stability.run_cycle(self)
        logger.info("odin_application_started")

    async def _mission_gc_loop(self) -> None:
        interval = self.settings.mission_gc_interval_seconds
        while True:
            try:
                await asyncio.sleep(interval)
                await self.mission_gc.run(self.mission_manager)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("mission_gc_loop_error", error=str(exc))

    async def shutdown(self) -> None:
        await self.execution_engine.stop()
        await self.stream_heartbeat.stop()
        if self._mission_gc_task:
            self._mission_gc_task.cancel()
            try:
                await self._mission_gc_task
            except asyncio.CancelledError:
                pass
        await self.mission_dispatcher.stop()
        await self.runtime_observers.stop_all()
        await self.mission_worker.stop()
        await self.worker_registry.disconnect()
        if self._learning_scheduler._task:
            await self._learning_scheduler.stop()
        await self.tool_memory.disconnect()
        await self.autonomous_loop.stop()
        await self.objective_manager.disconnect()
        await self.action_scheduler.stop()
        await self.workspace_memory.disconnect()
        await self.workflow_memory.disconnect()
        await self.knowledge_runtime.disconnect()
        await self.agent_society.disconnect()
        await self.agent_execution.disconnect()
        await self.vector_memory.disconnect()
        await self.project_os.disconnect()
        await self.runtime_guardian.disconnect()
        await self.local_ai.disconnect()
        await self.operator_relationship.disconnect()
        await self.continuity_runtime.disconnect()
        await self.federated_memory.disconnect()
        await self.world_simulation.disconnect()
        await self.federation_runtime.disconnect()
        await self.identity_store.disconnect()
        if getattr(self.settings, "local_cognition_enabled", True):
            await self.embedding_runtime.disconnect()
            await self.model_manager.disconnect()
        await self.cognitive_memory.disconnect()
        await self.mission_context.disconnect()
        await self.distributed_pubsub.disconnect()
        await self.distributed_queue.disconnect()
        if self._sqlite_execution_store:
            await self._sqlite_execution_store.disconnect()
        await self.live_loop.stop()
        await self.conscious_loop.stop()
        await self.watchers.stop_all()
        await self.runtime.stop()
        await self.orchestrator.stop()
        await self.memory.shutdown()
        await self.event_bus.disconnect()
        if self.redis_client:
            await self.redis_client.disconnect()
        logger.info("odin_application_shutdown")

    @property
    def memory_service(self) -> MimirCoordinator:
        return self.memory

    @property
    def workflow_engine(self) -> DAGWorkflowRunner:
        return self.workflow_runner


_app: OdinApplication | None = None


@lru_cache
def get_app() -> OdinApplication:
    global _app
    if _app is None:
        _app = OdinApplication()
    return _app
