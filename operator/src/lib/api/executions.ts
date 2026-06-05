import { apiFetch } from "./client";

export interface ExecutionRecord {
  execution_id: string;
  mission_id?: string | null;
  task_id?: string | null;
  executor_agent: string;
  capability_used: string;
  execution_type: string;
  state: string;
  lease_expiry?: string | null;
  created_at: string;
  started_at?: string | null;
  ended_at?: string | null;
  retry_count: number;
  max_retries: number;
  stdout_ref: string;
  stderr_ref: string;
  exit_code?: number | null;
  error?: string | null;
  params?: Record<string, unknown>;
  result?: Record<string, unknown>;
}

export interface ExecutionsListResponse {
  count: number;
  metrics: Record<string, number>;
  executions: ExecutionRecord[];
}

export interface ExecutionRunBody {
  capability: string;
  mission_id?: string;
  task_id?: string;
  executor_agent?: string;
  execution_type?: string;
  params?: Record<string, unknown>;
  timeout_seconds?: number;
  max_retries?: number;
}

export const executionsApi = {
  list: (limit = 50) =>
    apiFetch<ExecutionsListResponse>("/runtime/executions", { params: { limit } }),

  get: (id: string) => apiFetch<ExecutionRecord>(`/executions/${id}`),

  logs: (id: string, tail = 500) =>
    apiFetch<{ execution_id: string; stdout: string[]; stderr: string[] }>(
      `/executions/${id}/logs`,
      { params: { tail } }
    ),

  run: (body: ExecutionRunBody) =>
    apiFetch<ExecutionRecord>("/executions/run", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  cancel: (id: string) =>
    apiFetch<ExecutionRecord>(`/executions/${id}/cancel`, { method: "POST" }),

  retry: (id: string) =>
    apiFetch<ExecutionRecord>(`/executions/${id}/retry`, { method: "POST" }),
};
