export function CognitionViewer({ items }: { items: Array<Record<string, unknown>> }) {
  if (!items.length) {
    return <p className="text-odin-muted text-sm">No cognition events yet.</p>;
  }
  return (
    <div className="space-y-2 max-h-[520px] overflow-y-auto font-mono text-xs">
      {items.map((item) => (
        <div key={String(item.id)} className="rounded border border-odin-border bg-odin-bg px-3 py-2">
          <span className="text-odin-accent">{String(item.stage)}</span>
          <p className="text-slate-300 mt-1">{String(item.message)}</p>
          <p className="text-odin-muted mt-1">{String(item.timestamp ?? "")}</p>
        </div>
      ))}
    </div>
  );
}
