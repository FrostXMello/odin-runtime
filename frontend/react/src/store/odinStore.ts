import { create } from "zustand";
import { api, OdinEvent, PermissionRequest, SystemStatus, Task, WorkflowRun } from "@/lib/api";

interface OdinState {
  connected: boolean;
  loading: boolean;
  error: string | null;
  status: SystemStatus | null;
  agents: SystemStatus["agents"];
  tools: Array<{ name: string; description: string }>;
  workflows: WorkflowRun[];
  tasks: Task[];
  permissions: PermissionRequest[];
  events: OdinEvent[];
  auditLogs: Array<Record<string, unknown>>;
  cognition: Array<Record<string, unknown>>;
  runtimeStatus: Record<string, unknown> | null;
  runtimeAgents: Array<Record<string, unknown>>;
  browserSession: Record<string, unknown> | null;
  memoryClusters: Array<Record<string, unknown>>;
  watcherInsights: OdinEvent[];
  metrics: Record<string, unknown> | null;
  fetchAll: () => Promise<void>;
  addEvent: (e: OdinEvent) => void;
  submitObjective: (objective: string) => Promise<void>;
  refreshBrowser: () => Promise<void>;
}

export const useOdinStore = create<OdinState>((set, get) => ({
  connected: false,
  loading: false,
  error: null,
  status: null,
  agents: [],
  tools: [],
  workflows: [],
  tasks: [],
  permissions: [],
  events: [],
  auditLogs: [],
  cognition: [],
  runtimeStatus: null,
  runtimeAgents: [],
  browserSession: null,
  memoryClusters: [],
  watcherInsights: [],
  metrics: null,

  fetchAll: async () => {
    set({ loading: true, error: null });
    try {
      await api.health();
      const [
        status,
        agents,
        tools,
        workflows,
        tasks,
        permissions,
        audit,
        cognition,
        runtimeStatus,
        runtimeAgents,
        clusters,
        watcherInsights,
        metrics,
      ] = await Promise.all([
        api.status(),
        api.agents(),
        api.tools(),
        api.workflows.list().catch(() => []),
        api.tasks.list().catch(() => []),
        api.permissions.pending().catch(() => []),
        api.observability.audit(50).catch(() => []),
        api.cognition.recent(50).catch(() => []),
        api.runtime.status().catch(() => null),
        api.runtime.agents().catch(() => []),
        api.memory.clusters().catch(() => []),
        api.watchers.insights(30).catch(() => []),
        api.observability.metrics().catch(() => null),
      ]);
      set({
        connected: true,
        status,
        agents,
        tools,
        workflows,
        tasks,
        permissions,
        auditLogs: audit,
        cognition,
        runtimeStatus,
        runtimeAgents,
        memoryClusters: clusters,
        watcherInsights,
        metrics,
        loading: false,
      });
    } catch (e) {
      set({
        connected: false,
        loading: false,
        error: e instanceof Error ? e.message : "Backend unreachable",
      });
    }
  },

  addEvent: (e) =>
    set((s) => {
      const events = [e, ...s.events].slice(0, 200);
      const cognition =
        e.type === "cognition.progress"
          ? [e.payload as Record<string, unknown>, ...s.cognition].slice(0, 100)
          : s.cognition;
      return { events, cognition };
    }),

  submitObjective: async (objective) => {
    await api.objectives.submit(objective, true);
    await get().fetchAll();
  },

  refreshBrowser: async () => {
    const session = await api.browser.session();
    set({ browserSession: session });
  },
}));
