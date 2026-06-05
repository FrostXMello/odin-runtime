export function SandboxViewer({
  snapshots,
}: {
  snapshots: Array<{ tool_name?: string; rollback_available?: boolean }>;
}) {
  if (!snapshots.length) {
    return <p className="text-odin-muted text-sm">No sandbox executions recorded.</p>;
  }
  return (
    <ul className="space-y-2 text-sm">
      {snapshots.map((s, i) => (
        <li key={i} className="rounded border border-odin-border px-3 py-2">
          <span className="font-mono text-odin-accent">{s.tool_name ?? "unknown"}</span>
          {s.rollback_available && (
            <span className="ml-2 text-xs text-green-400">rollback available</span>
          )}
        </li>
      ))}
    </ul>
  );
}
