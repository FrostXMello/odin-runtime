const BASE = import.meta.env.VITE_ODIN_API ?? "/api/v1";

export async function odinFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json() as Promise<T>;
}

export const desktopApi = {
  connect: () => odinFetch("/runtime/desktop-client/connect", { method: "POST" }),
  setMode: (mode: string) =>
    odinFetch("/runtime/desktop-client/mode", { method: "POST", body: JSON.stringify({ mode }) }),
  openWorkspace: () => odinFetch("/runtime/conversation-workspace/open", { method: "POST", body: "{}" }),
  renderViz: (view: string) =>
    odinFetch("/runtime/live-visualization/render", {
      method: "POST",
      body: JSON.stringify({ view }),
    }),
  startup: () => odinFetch("/runtime/operator-experience/startup", { method: "POST" }),
};
