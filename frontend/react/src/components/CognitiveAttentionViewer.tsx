export function CognitiveAttentionViewer({
  items,
}: {
  items: Array<{ message: string; priority: string; source: string; reason: string }>;
}) {
  if (!items.length) {
    return <p className="text-odin-muted text-sm">No active attention items.</p>;
  }
  return (
    <ul className="space-y-2 max-w-xl">
      {items.map((a, i) => (
        <li
          key={i}
          className={`rounded-lg border px-4 py-3 text-sm ${
            a.priority === "critical" ? "border-red-500/40 bg-red-500/10" : "border-odin-border"
          }`}
        >
          <span className="text-xs text-odin-accent uppercase">{a.priority}</span>
          <p className="mt-1">{a.message}</p>
          <p className="text-xs text-odin-muted mt-1">{a.reason}</p>
        </li>
      ))}
    </ul>
  );
}
