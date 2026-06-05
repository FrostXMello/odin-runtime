export const EVENT_COLORS: Record<string, string> = {
  mission_created: "#8b5cf6",
  mission_dispatched: "#3b82f6",
  task_assigned: "#22d3ee",
  task_started: "#06b6d4",
  task_completed: "#10b981",
  task_failed: "#f43f5e",
  retry_triggered: "#f59e0b",
  escalation_triggered: "#fb7185",
  policy_blocked: "#ef4444",
  memory_mutated: "#a78bfa",
  signal_propagated: "#38bdf8",
  signal_suppressed: "#64748b",
  duplicate_suppressed: "#94a3b8",
  state_transition: "#6366f1",
  escalation: "#fb7185",
  adaptation: "#fcd34d",
  history: "#475569",
  task_state_transition: "#14b8a6",
};

export function eventColor(kind: string): string {
  if (EVENT_COLORS[kind]) return EVENT_COLORS[kind];
  if (kind.includes("fail")) return EVENT_COLORS.task_failed;
  if (kind.includes("policy")) return EVENT_COLORS.policy_blocked;
  if (kind.includes("signal")) return EVENT_COLORS.signal_propagated;
  return "#64748b";
}

export const EVENT_FILTERS = [
  "all",
  "mission",
  "task",
  "policy",
  "retry",
  "escalation",
  "memory",
  "signal",
] as const;

export type EventFilter = (typeof EVENT_FILTERS)[number];

export function matchesFilter(kind: string, filter: EventFilter): boolean {
  if (filter === "all") return true;
  if (filter === "mission") return kind.startsWith("mission") || kind === "state_transition";
  if (filter === "task") return kind.startsWith("task") || kind === "history";
  if (filter === "policy") return kind.includes("policy");
  if (filter === "retry") return kind.includes("retry");
  if (filter === "escalation") return kind.includes("escalat");
  if (filter === "memory") return kind.includes("memory");
  if (filter === "signal") return kind.includes("signal");
  return true;
}
