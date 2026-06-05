/** WebSocket stream envelope (matches backend StreamEnvelope). */

export type StreamEventKind =
  | "mission_created"
  | "mission_state_changed"
  | "mission_dispatched"
  | "task_assigned"
  | "task_started"
  | "task_completed"
  | "task_failed"
  | "retry_triggered"
  | "escalation_triggered"
  | "signal_propagated"
  | "signal_suppressed"
  | "memory_mutated"
  | "policy_blocked"
  | "health_changed"
  | "bottleneck_detected"
  | "duplicate_suppressed"
  | "heartbeat"
  | "connected"
  | "execution_allocated"
  | "execution_started"
  | "execution_progress"
  | "execution_stdout"
  | "execution_stderr"
  | "execution_completed"
  | "execution_failed"
  | "execution_cancelled"
  | "execution_timeout"
  | "execution_retry"
  | "execution_rollback"
  | "execution_submitted_async"
  | "execution_callback_received"
  | "dependency_released"
  | "mission_resumed"
  | "graph_reconciled"
  | "runtime_lock_wait"
  | "runtime_lock_acquired"
  | "async_wave_dispatched"
  | "queue_enqueued"
  | "queue_restored"
  | "lease_recovered"
  | "execution_recovered"
  | "orphan_detected"
  | "task_requeued"
  | "deadlettered"
  | "replay_suppressed";

export interface StreamEnvelope {
  event_id: string;
  event_type: StreamEventKind;
  channel: string;
  timestamp: string;
  trace_id?: string | null;
  span_id?: string | null;
  parent_span_id?: string | null;
  causal_chain_id?: string | null;
  mission_id?: string | null;
  task_id?: string | null;
  execution_id?: string | null;
  workflow_id?: string | null;
  agent_id?: string | null;
  component: string;
  message: string;
  payload?: Record<string, unknown>;
  latency_ms?: number | null;
}

export type StreamConnectionStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "stale"
  | "offline";
