/** Lifecycle noise — visible in full stream but excluded from issue-style panels. */
const LIFECYCLE_NOISE = new Set([
  "heartbeat",
  "connected",
  "state_transition",
  "mission_state_changed",
  "mission_dispatched",
  "mission_created",
  "lease_recovered",
  "retry_attempt",
  "retry_triggered",
  "idle",
  "runtime_health_inspected",
  "runtime_sync_validated",
  "checkpoint_integrity_verified",
  "runtime_metrics_generated",
  "startup_performance_measured",
  "stream_anomaly_detected",
]);

const ISSUE_SIGNALS = new Set([
  "mission_failed",
  "task_failed",
  "system_error",
  "mission_blocked",
  "mission_blocked_persistent",
  "policy_blocked",
  "execution_failed",
  "crash",
]);

export function isLifecycleNoise(eventType: string): boolean {
  return LIFECYCLE_NOISE.has(eventType.toLowerCase());
}

export function isIssueSignal(eventType: string): boolean {
  const kind = eventType.toLowerCase();
  if (ISSUE_SIGNALS.has(kind)) return true;
  return kind.includes("failed") || kind.includes("crash") || kind.includes("error");
}

export function isCriticalFinding(severity: string): boolean {
  return severity.toLowerCase() === "critical";
}
