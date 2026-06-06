const BASE = import.meta.env.VITE_ODIN_API ?? "/api/v1";

export async function odinFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json() as Promise<T>;
}

export const workspaceApi = {
  open: (mode = "operator") =>
    odinFetch("/runtime/cognitive-workspace/open", { method: "POST", body: JSON.stringify({ mode }) }),
  renderReasoning: (thought: string) =>
    odinFetch("/runtime/reasoning-live/render", { method: "POST", body: JSON.stringify({ thought }) }),
  presenceTurn: (text: string) =>
    odinFetch("/runtime/conversational-presence/turn", { method: "POST", body: JSON.stringify({ text }) }),
};
