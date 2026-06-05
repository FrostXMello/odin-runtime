import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Props {
  onClose: () => void;
}

export function CommandPalette({ onClose }: Props) {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [actions, setActions] = useState<Array<{ id: string; label: string; prompt: string }>>([]);
  const [insight, setInsight] = useState<string | null>(null);

  useEffect(() => {
    api.ambient
      .overlayActions()
      .then((r) => {
        setActions(r.actions);
        setInsight(r.insight ?? null);
      })
      .catch(() => {});
  }, []);

  const submit = async (text?: string) => {
    const msg = (text ?? query).trim();
    if (!msg) return;
    setLoading(true);
    try {
      const res = await api.conversation.chat(msg, sessionId ?? undefined, true);
      setSessionId(res.session_id);
      setResponse(
        `Plan: ${res.plan?.steps?.length ?? 0} steps · Run: ${res.run_status ?? "n/a"}\n` +
          (res.reflection?.findings?.join("\n") ?? "")
      );
      if (!text) setQuery("");
    } catch (e) {
      setResponse(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-start justify-center pt-[12vh] z-50">
      <div className="w-[680px] rounded-xl border border-odin-border bg-odin-panel shadow-2xl p-4">
        {insight && (
          <p className="text-xs text-odin-muted mb-2 border-b border-odin-border pb-2">{insight}</p>
        )}
        <input
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
            if (e.key === "Escape") onClose();
          }}
          placeholder="Ask ODIN anything… (Alt+Space)"
          className="w-full bg-odin-bg border border-odin-border rounded-lg px-4 py-3 text-sm outline-none focus:border-odin-accent"
        />
        {actions.length > 1 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {actions
              .filter((a) => a.id !== "ask")
              .map((a) => (
                <button
                  key={a.id}
                  onClick={() => {
                    setQuery(a.prompt);
                    if (a.prompt) submit(a.prompt);
                  }}
                  className="px-3 py-1 rounded-full text-xs border border-odin-border hover:border-odin-accent text-odin-muted hover:text-odin-accent"
                >
                  {a.label}
                </button>
              ))}
          </div>
        )}
        {loading && <p className="text-xs text-odin-muted mt-2">Thinking…</p>}
        {response && (
          <pre className="mt-3 text-xs text-slate-300 whitespace-pre-wrap max-h-40 overflow-y-auto">
            {response}
          </pre>
        )}
      </div>
    </div>
  );
}
