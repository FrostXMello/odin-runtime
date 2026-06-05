import type { QueryClient } from "@tanstack/react-query";
import type { StreamEnvelope } from "./types";
import type {
  BottleneckReport,
  MissionTimeline,
  RuntimeHealthResponse,
  TimelineEntry,
  TraceDetail,
  TraceEventRecord,
} from "@/lib/api/types";

function envelopeToTimelineEntry(env: StreamEnvelope, sortKey: number): TimelineEntry {
  return {
    timestamp: env.timestamp,
    kind: env.event_type,
    source: env.component,
    message: env.message,
    trace_id: env.trace_id,
    span_id: env.span_id,
    agent_id: env.agent_id,
    task_id: env.task_id,
    payload: env.payload,
    sort_key: sortKey,
  };
}

export function applyStreamEnvelope(qc: QueryClient, env: StreamEnvelope): void {
  const { event_type: kind } = env;

  if (kind === "health_changed" && env.payload) {
    qc.setQueryData<RuntimeHealthResponse>(["runtime", "health"], (prev) => {
      if (!prev) return prev;
      const status = (env.payload?.status as string) ?? prev.orchestration?.status;
      return {
        ...prev,
        orchestration: prev.orchestration
          ? { ...prev.orchestration, status: status as RuntimeHealthResponse["orchestration"]["status"] }
          : prev.orchestration,
      };
    });
  }

  if (kind === "bottleneck_detected" && env.mission_id) {
    qc.setQueryData<{ count: number; bottlenecks: BottleneckReport[] }>(
      ["runtime", "bottlenecks"],
      (prev) => {
        const bottlenecks = prev?.bottlenecks ?? [];
        const next: BottleneckReport = {
          mission_id: env.mission_id!,
          reason: env.message,
          pending_tasks: Number(env.payload?.pending_tasks ?? 0),
          blocked_tasks: Number(env.payload?.blocked_tasks ?? 0),
          state: String(env.payload?.state ?? ""),
        };
        const filtered = bottlenecks.filter((b) => b.mission_id !== next.mission_id);
        return { count: filtered.length + 1, bottlenecks: [next, ...filtered].slice(0, 20) };
      }
    );
  }

  if (env.mission_id && kind === "mission_state_changed") {
    const toState = String(env.payload?.to_state ?? "");
    qc.setQueryData<MissionTimeline>(["mission-timeline", env.mission_id], (prev) => {
      if (!prev) return prev;
      const entry = envelopeToTimelineEntry(env, Date.now());
      return {
        ...prev,
        current_state: toState || prev.current_state,
        entry_count: prev.entry_count + 1,
        entries: [entry, ...prev.entries],
      };
    });
    qc.invalidateQueries({ queryKey: ["missions"], refetchType: "none" });
  }

  if (env.mission_id && kind !== "heartbeat" && kind !== "connected") {
    qc.setQueryData<MissionTimeline>(["mission-timeline", env.mission_id], (prev) => {
      if (!prev) return prev;
      const entry = envelopeToTimelineEntry(env, Date.now());
      if (prev.entries.some((e) => e.message === entry.message && e.kind === entry.kind && e.timestamp === entry.timestamp)) {
        return prev;
      }
      return {
        ...prev,
        entry_count: prev.entry_count + 1,
        entries: [entry, ...prev.entries],
      };
    });
  }

  if (env.trace_id && kind !== "heartbeat" && kind !== "connected") {
    qc.setQueryData<TraceDetail>(["trace", env.trace_id], (prev) => {
      if (!prev?.events) return prev;
      const exists = prev.events.some((e) => e.event_id === env.event_id);
      if (exists) return prev;
      const record: TraceEventRecord = {
        event_id: env.event_id,
        kind: env.event_type,
        timestamp: env.timestamp,
        message: env.message,
        component: env.component,
        trace_id: env.trace_id!,
        span_id: env.span_id ?? "",
        parent_span_id: env.parent_span_id,
        causal_chain_id: env.causal_chain_id ?? prev.causal_chain_id,
        mission_id: env.mission_id,
        task_id: env.task_id,
        payload: env.payload ?? {},
        duration_ms: env.latency_ms,
      };
      return {
        ...prev,
        event_count: prev.event_count + 1,
        events: [...prev.events, record],
      };
    });
  }

  if (
    kind === "mission_created" ||
    kind === "mission_dispatched" ||
    kind === "task_completed" ||
    kind === "task_failed"
  ) {
    qc.invalidateQueries({ queryKey: ["runtime", "health"], refetchType: "none" });
    qc.invalidateQueries({ queryKey: ["runtime", "introspection"], refetchType: "none" });
    qc.invalidateQueries({ queryKey: ["missions"], refetchType: "none" });
  }

  if (kind === "signal_propagated" || kind === "signal_suppressed") {
    qc.invalidateQueries({ queryKey: ["signal-graph"], refetchType: "none" });
  }
}
