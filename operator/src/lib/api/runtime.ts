import { apiFetch } from "./client";
import type {
  BottleneckReport,
  CommandResponse,
  CausalEventsResponse,
  MemoryMutation,
  MissionSummary,
  MissionTimeline,
  QueueSnapshot,
  RuntimeHealthResponse,
  RuntimeIntrospectionResponse,
  SignalGraphExport,
  TraceDetail,
  WorkerSnapshot,
} from "./types";

export const runtimeApi = {
  health: () => apiFetch<RuntimeHealthResponse>("/runtime/health"),

  introspection: () =>
    apiFetch<RuntimeIntrospectionResponse>("/runtime/introspection"),

  queues: () => apiFetch<QueueSnapshot>("/runtime/queues"),

  workers: () =>
    apiFetch<{ workers: WorkerSnapshot; agents: Array<{ agent_id: string; status: string }> }>(
      "/runtime/workers"
    ),

  bottlenecks: () =>
    apiFetch<{ count: number; bottlenecks: BottleneckReport[] }>("/runtime/bottlenecks"),

  signalGraph: (limit = 500) =>
    apiFetch<SignalGraphExport>("/runtime/signal-graph", { params: { limit } }),

  missions: (limit = 50) =>
    apiFetch<MissionSummary[]>("/missions", { params: { limit } }),

  createMission: (body: {
    objective: string;
    priority?: number;
    autonomy_level?: number;
    human_approved?: boolean;
    start_worker?: boolean;
  }) =>
    apiFetch<CommandResponse>("/missions/create", {
      method: "POST",
      body: JSON.stringify({
        priority: 50,
        autonomy_level: 1,
        human_approved: false,
        start_worker: true,
        ...body,
      }),
    }),

  resumeMission: (missionId: string) =>
    apiFetch<{ mission_id: string; state: string }>(`/missions/${missionId}/resume`, {
      method: "POST",
    }),

  pauseMission: (missionId: string) =>
    apiFetch<{ mission_id: string; state: string }>(`/missions/${missionId}/pause`, {
      method: "POST",
    }),

  recoverSession: () =>
    apiFetch<Record<string, unknown>>("/runtime/session-persistence-v2/recover", {
      method: "POST",
    }),

  p64RuntimeHealth: () =>
    apiFetch<Record<string, unknown>>("/runtime/runtime-health"),

  missionTimeline: (missionId: string) =>
    apiFetch<MissionTimeline>(`/missions/${missionId}/timeline`),

  taskTimeline: (taskId: string) =>
    apiFetch<MissionTimeline & { task_id?: string; goal?: string; status?: string }>(
      `/tasks/${taskId}/timeline`
    ),

  missionTaskTimeline: (missionId: string, taskId: string) =>
    apiFetch<MissionTimeline>(`/missions/${missionId}/tasks/${taskId}/timeline`),

  trace: (traceId: string) => apiFetch<TraceDetail>(`/traces/${traceId}`),

  causalEvents: (limit = 100) =>
    apiFetch<CausalEventsResponse>("/observability/traces", { params: { limit } }),

  memoryMutations: (limit = 100) =>
    apiFetch<MemoryMutation[]>("/observability/memory-mutations", { params: { limit } }),

  metrics: () => apiFetch<Record<string, unknown>>("/observability/metrics"),

  executions: (limit = 50) =>
    apiFetch<{
      count: number;
      metrics: Record<string, number>;
      active_mission_executions: Array<{
        mission_id: string;
        task_id: string;
        execution_id: string;
        state: string;
      }>;
    }>("/runtime/executions", { params: { limit } }),

  dependencies: () =>
    apiFetch<{ mission_count: number; graphs: unknown[] }>("/runtime/dependencies"),

  topology: () => apiFetch<Record<string, unknown>>("/runtime/topology"),

  routing: () =>
    apiFetch<{
      recent_decisions: Array<Record<string, unknown>>;
      targets: Array<Record<string, unknown>>;
    }>("/runtime/routing"),

  pools: () =>
    apiFetch<{ pools: Record<string, Record<string, number>>; default: string }>("/runtime/pools"),

  workersRegistry: () =>
    apiFetch<{ workers: Array<Record<string, unknown>>; local_worker_id: string }>(
      "/runtime/workers/registry"
    ),

  drainWorker: (workerId: string) =>
    apiFetch<{ worker_id: string; draining: boolean }>(`/runtime/workers/${workerId}/drain`, {
      method: "POST",
    }),
};
