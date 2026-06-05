export function KernelStateViewer({ state }: { state: Record<string, unknown> | null }) {
  if (!state) {
    return <p className="text-odin-muted text-sm">Loading cognitive kernel…</p>;
  }
  return (
    <div className="space-y-4 max-w-2xl text-sm">
      <div className="rounded-lg border border-odin-accent/30 bg-odin-accent/10 p-4">
        <p className="text-xs text-odin-muted uppercase">Current focus</p>
        <p className="text-lg text-odin-accent mt-1">{String(state.current_focus)}</p>
      </div>
      <div>
        <p className="text-odin-muted text-xs uppercase mb-2">Priority queue</p>
        <ul className="space-y-1">
          {((state.priority_tasks as Array<Record<string, unknown>>) || []).slice(0, 8).map((t, i) => (
            <li key={i} className="flex justify-between border-b border-odin-border/50 py-1">
              <span>{String(t.title)}</span>
              <span className="text-odin-muted">{Number(t.score).toFixed(2)}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <span className="text-odin-muted">Signals processed</span>
        <span>{String(state.signal_count)}</span>
        <span className="text-odin-muted">System health</span>
        <span>{String((state.system_health as Record<string, unknown>)?.status ?? "—")}</span>
      </div>
    </div>
  );
}
