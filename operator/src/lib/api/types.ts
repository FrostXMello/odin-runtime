/** Typed shapes from Odin observability + runtime APIs */

export type HealthStatus = "healthy" | "degraded" | "critical" | string;

export interface OrchestrationHealth {
  status: HealthStatus;
  execution_throughput: number;
  completion_rate: number;
  stuck_mission_count: number;
  duplicate_suppression_count: number;
  active_execution_count: number;
  retry_frequency: number;
  escalation_rate: number;
  worker_responsive: boolean;
  queue_depth: number;
  pickup_latency_ms: number;
  worker_utilization: number;
  zero_throughput: boolean;
  duplicate_loop_detected: boolean;
  warnings: string[];
}

export interface RootCauseFinding {
  issue: string;
  probable_cause: string;
  affected_components: string[];
  recommended_action: string;
  severity: "low" | "medium" | "high" | "critical" | string;
  evidence: Record<string, unknown>;
}

export interface RootCauseAnalysis {
  generated_at: string;
  status: HealthStatus;
  findings: RootCauseFinding[];
  summary: string;
}

export interface RuntimeHealthResponse {
  status: string;
  system_health: HealthStatus;
  orchestration: OrchestrationHealth;
  root_cause_analysis: RootCauseAnalysis;
  missions: {
    active_missions: number;
    dispatchable_missions: number;
    queue_depth: number;
    duplicate_suppressed_count?: number;
    duplicate_detected_count?: number;
    dispatcher: Record<string, unknown>;
    runtime_metrics: Record<string, number>;
    gc?: Record<string, number>;
  };
  recursion_events_detected: number;
  suppressed_signal_count: number;
  kernel_processing_rate: number;
  active_signal_chains: number;
  signal_count: number;
  runtime_loop_health: string;
}

export interface RuntimeIntrospectionResponse {
  introspection: {
    active_missions: number;
    dispatchable_missions: number;
    queue_depth: number;
    dispatcher: Record<string, unknown>;
    executing_tasks: TaskRef[];
    blocked_tasks: TaskRef[];
    pending_tasks: TaskRef[];
    policy_blocked_missions: Array<{ mission_id: string; objective: string }>;
    retry_queue_size: number;
    trace_store: Record<string, number>;
  };
  diagnostics: RootCauseAnalysis;
  metrics: Record<string, unknown>;
}

export interface TaskRef {
  mission_id: string;
  task_id: string;
  goal: string;
  status: string;
  agent?: string | null;
}

export interface QueueSnapshot {
  dispatch_queue_depth: number;
  retry_queue_depth: number;
  due_missions: string[];
}

export interface WorkerSnapshot {
  dispatcher_running: boolean;
  dispatcher_ticks: number;
  dispatcher_executions: number;
  worker_mode: string;
  last_tick_at: number | null;
}

export interface BottleneckReport {
  mission_id: string;
  reason: string;
  pending_tasks: number;
  blocked_tasks: number;
  state: string;
}

export interface TimelineEntry {
  timestamp: string;
  kind: string;
  source: string;
  message: string;
  trace_id?: string | null;
  span_id?: string | null;
  agent_id?: string | null;
  task_id?: string | null;
  payload?: Record<string, unknown>;
  sort_key: number;
}

export interface MissionTimeline {
  mission_id: string;
  trace_id?: string | null;
  causal_chain_id?: string | null;
  current_state: string;
  entry_count: number;
  entries: TimelineEntry[];
  checkpoints?: unknown[];
  memory_mutations?: MemoryMutation[];
}

export interface MemoryMutation {
  mutation_id: string;
  timestamp: string;
  trace_id?: string | null;
  mission_id?: string | null;
  task_id?: string | null;
  actor: string;
  reason: string;
  category: string;
  memory_id?: string | null;
  previous_hash?: string | null;
  new_hash?: string | null;
  rollback_ref?: string | null;
  metadata?: Record<string, unknown>;
}

export interface SignalGraphNode {
  id: string;
  kind: string;
  label: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface SignalGraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface SignalGraphExport {
  generated_at: string;
  node_count: number;
  edge_count: number;
  nodes: SignalGraphNode[];
  edges: SignalGraphEdge[];
}

export interface TraceEventRecord {
  event_id: string;
  kind: string;
  timestamp: string;
  trace_id: string;
  span_id: string;
  parent_span_id?: string | null;
  causal_chain_id: string;
  mission_id?: string | null;
  task_id?: string | null;
  component: string;
  message: string;
  payload?: Record<string, unknown>;
  duration_ms?: number | null;
}

export interface TraceDetail {
  trace_id: string;
  causal_chain_id: string;
  event_count: number;
  started_at: string;
  ended_at: string;
  events: TraceEventRecord[];
}

export interface MissionSummary {
  mission_id: string;
  objective: string;
  current_state: string;
  priority: number;
  active_tasks: Array<Record<string, unknown>>;
  completed_tasks: Array<Record<string, unknown>>;
}

export interface CausalEventsResponse {
  execution_traces: unknown[];
  causal_events: TraceEventRecord[];
  store_stats: Record<string, number>;
}
