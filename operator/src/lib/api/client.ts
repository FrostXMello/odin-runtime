/**
 * Typed API client — all requests proxied via Next.js to Odin backend.
 * WebSocket-ready: use createEventSource() for future live streams.
 */

const API_BASE =
  typeof window !== "undefined"
    ? "/api/v1"
    : `${process.env.ODIN_BACKEND_URL ?? "http://127.0.0.1:8000"}/api/v1`;

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit & { params?: Record<string, string | number> }
): Promise<T> {
  let url = `${API_BASE}${path}`;
  if (options?.params) {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(options.params)) {
      q.set(k, String(v));
    }
    url += `?${q}`;
  }
  const { params: _p, ...init } = options ?? {};
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(text || `HTTP ${res.status}`, res.status, text);
  }
  return res.json() as Promise<T>;
}

/** SSE — websocket-ready architecture; same origin via proxy */
export function createEventSource(
  path = "/events/stream",
  onEvent: (data: unknown) => void
): EventSource {
  const url = `${API_BASE}${path}`;
  const es = new EventSource(url);
  es.onmessage = (msg) => {
    try {
      onEvent(JSON.parse(msg.data));
    } catch {
      /* heartbeat */
    }
  };
  return es;
}
