/** Resolve WebSocket base URL (Next rewrites do not proxy WS). */

export function wsBaseUrl(): string {
  const env = process.env.NEXT_PUBLIC_WS_BASE?.replace(/\/$/, "");
  if (env) return env;
  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    const wsProto = protocol === "https:" ? "wss:" : "ws:";
    return `${wsProto}//${hostname}:8000/api/v1/ws`;
  }
  return "ws://127.0.0.1:8000/api/v1/ws";
}

export function wsChannelUrl(path: string): string {
  const base = wsBaseUrl();
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}${p}`;
}
