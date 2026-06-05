const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export interface SystemStatus {
  orchestrator: string;
  running: boolean;
  active_tasks: number;
  agents: Array<{
    id: string;
    name: string;
    description: string;
    state: string;
  }>;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  assigned_agent: string | null;
}

export interface WorkflowRun {
  id: string;
  objective: string;
  status: string;
  current_step: number;
  step_results: Record<string, unknown>;
  error?: string;
}

export interface PermissionRequest {
  id: string;
  tool_name: string;
  agent_id: string;
  permission_class: string;
  reason: string;
}

export interface OdinEvent {
  id: string;
  type: string;
  source: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

export const api = {
  health: () => request<{ status: string; version: string; redis: boolean }>("/health"),
  status: () => request<SystemStatus>("/status"),
  agents: () => request<SystemStatus["agents"]>("/agents"),
  tools: () => request<Array<{ name: string; description: string }>>("/tools"),
  tasks: {
    list: (status?: string) =>
      request<Task[]>(`/tasks${status ? `?status=${status}` : ""}`),
    create: (body: { title: string; description?: string; metadata?: Record<string, unknown> }) =>
      request<Task>("/tasks", { method: "POST", body: JSON.stringify(body) }),
    get: (id: string) => request<Task>(`/tasks/${id}`),
  },
  objectives: {
    submit: (objective: string, execute = true) =>
      request<{
        plan_id: string;
        objective: string;
        steps: Array<Record<string, unknown>>;
        run_id: string | null;
        run_status: string | null;
      }>("/objectives", {
        method: "POST",
        body: JSON.stringify({ objective, execute }),
      }),
  },
  workflows: {
    list: () => request<WorkflowRun[]>("/workflows"),
    get: (id: string) => request<WorkflowRun>(`/workflows/${id}`),
  },
  memory: {
    search: (query: string, limit = 5) =>
      request<Array<Record<string, unknown>>>("/memory/search", {
        method: "POST",
        body: JSON.stringify({ query, limit }),
      }),
    save: (content: string, category = "general") =>
      request<{ memory_id: string }>("/memory", {
        method: "POST",
        body: JSON.stringify({ content, category }),
      }),
    clusters: () => request<Array<Record<string, unknown>>>("/memory/clusters"),
  },
  permissions: {
    pending: () => request<PermissionRequest[]>("/permissions/pending"),
    approve: (requestId: string) =>
      request<PermissionRequest>("/permissions/approve", {
        method: "POST",
        body: JSON.stringify({ request_id: requestId }),
      }),
  },
  observability: {
    traces: (limit = 50) => request<Array<Record<string, unknown>>>(`/observability/traces?limit=${limit}`),
    audit: (limit = 100) => request<Array<Record<string, unknown>>>(`/observability/audit?limit=${limit}`),
    events: (limit = 100) => request<OdinEvent[]>(`/observability/events/recent?limit=${limit}`),
    metrics: () => request<Record<string, unknown>>("/observability/metrics"),
  },
  runtime: {
    status: () => request<Record<string, unknown>>("/runtime/status"),
    agents: () => request<Array<Record<string, unknown>>>("/runtime/agents"),
  },
  browser: {
    tabs: () => request<Array<Record<string, unknown>>>("/browser/tabs"),
    session: () => request<Record<string, unknown>>("/browser/session"),
  },
  cognition: {
    recent: (limit = 100) => request<Array<Record<string, unknown>>>(`/cognition/recent?limit=${limit}`),
  },
  context: {
    get: () => request<Record<string, unknown>>("/context"),
    update: (body: Record<string, unknown>) =>
      request<Record<string, unknown>>("/context", { method: "PATCH", body: JSON.stringify(body) }),
  },
  watchers: {
    insights: (limit = 50) => request<OdinEvent[]>(`/watchers/insights/recent?limit=${limit}`),
  },
  conversation: {
    start: () => request<{ id: string }>("/conversation/sessions", { method: "POST" }),
    chat: (message: string, sessionId?: string, execute = true) =>
      request<{
        session_id: string;
        plan: { steps: unknown[] };
        run_id: string | null;
        run_status: string | null;
        reflection: { findings: string[]; recommendations: string[] } | null;
      }>("/conversation/chat", {
        method: "POST",
        body: JSON.stringify({ message, session_id: sessionId, execute }),
      }),
    getSession: (id: string) => request<{ messages: Array<{ role: string; content: string }> }>(
      `/conversation/sessions/${id}`
    ),
  },
  knowledgeGraph: {
    search: (q: string) => request<Array<Record<string, unknown>>>(`/knowledge-graph/search?q=${encodeURIComponent(q)}`),
    projectMap: (id: string) =>
      request<Record<string, unknown>>(`/knowledge-graph/project/${id}/dependencies`),
  },
  reflection: {
    get: (workflowId: string) => request<Record<string, unknown>>(`/reflection/${workflowId}`),
  },
  persistentWorkflows: {
    list: () => request<Array<Record<string, unknown>>>("/persistent-workflows"),
  },
  contextEngine: {
    get: () => request<{ enabled: boolean; session: Record<string, unknown> | null; explain: Record<string, unknown> }>("/context-engine"),
    update: (body: Record<string, unknown>) =>
      request<Record<string, unknown>>("/context-engine", { method: "PATCH", body: JSON.stringify(body) }),
  },
  ambient: {
    desktopSummary: () => request<Record<string, unknown>>("/desktop-semantics/summary"),
    cognitiveTimeline: (limit = 50) =>
      request<{ timeline: Array<Record<string, unknown>>; active_paths: Array<Record<string, unknown>> }>(
        `/cognitive-stream/timeline?limit=${limit}`
      ),
    reliability: () => request<Array<Record<string, unknown>>>("/execution-intelligence/reliability"),
    recommendations: () =>
      request<Array<{ id: string; title: string; message: string; category: string }>>("/proactive/recommendations"),
    dismissRecommendation: (id: string) =>
      request<{ dismissed: boolean }>(`/proactive/recommendations/${id}/dismiss`, { method: "POST" }),
    collaborationChains: () =>
      request<Array<{ id: string; objective: string; steps: Array<{ agent: string; description: string }> }>>(
        "/collaboration/chains"
      ),
    localModels: () => request<Record<string, unknown>>("/local-models/status"),
    overlayActions: () =>
      request<{ actions: Array<{ id: string; label: string; prompt: string }>; insight?: string }>(
        "/overlay/actions"
      ),
    consolidateMemory: () => request<Record<string, unknown>>("/memory/consolidate", { method: "POST" }),
    policies: () => request<Array<Record<string, unknown>>>("/policies"),
  },
  desktopRuntime: {
    get: () => request<Record<string, unknown>>("/desktop-runtime"),
    enable: (enabled: boolean) =>
      request<Record<string, unknown>>("/desktop-runtime", {
        method: "PATCH",
        body: JSON.stringify({ enabled }),
      }),
    ingest: (snapshot: Record<string, unknown>) =>
      request<Record<string, unknown>>("/desktop-runtime/ingest", {
        method: "POST",
        body: JSON.stringify(snapshot),
      }),
  },
  kernel: {
    state: () => request<Record<string, unknown>>("/kernel/state"),
    priority: () => request<{ items: Array<Record<string, unknown>>; current_focus: string }>("/kernel/priority"),
    graph: () => request<Record<string, unknown>>("/kernel/graph"),
    explain: () => request<Record<string, unknown>>("/kernel/explain"),
  },
  environment: {
    workspaceSummary: () => request<Record<string, unknown>>("/workspace-intelligence/summary"),
    liveCognition: () =>
      request<{
        attention: Array<Record<string, unknown>>;
        operational: Record<string, unknown>;
      }>("/live-cognition/state"),
    resilience: () => request<{ circuit_breakers: Array<Record<string, unknown>> }>("/resilience/status"),
    agentSociety: () => request<{ agents: Array<Record<string, unknown>> }>("/agent-society"),
    compute: () => request<Record<string, unknown>>("/compute/dashboard"),
    memoryTimeline: (limit = 50) =>
      request<Array<Record<string, unknown>>>(`/memory-evolution/timeline?limit=${limit}`),
    trustDashboard: () => request<Record<string, unknown>>("/trust/dashboard"),
    workspaceActions: () => request<Record<string, unknown>>("/workspace-automation/actions"),
  },
};

export function createEventSource(onEvent: (event: OdinEvent) => void): EventSource {
  const url = `${API_BASE}/events/stream`;
  const es = new EventSource(url);
  es.onmessage = (msg) => {
    try {
      const data = JSON.parse(msg.data) as OdinEvent;
      if (data.type) onEvent(data);
    } catch {
      /* ping */
    }
  };
  return es;
}
