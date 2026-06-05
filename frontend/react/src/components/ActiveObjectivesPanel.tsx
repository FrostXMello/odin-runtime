export function ActiveObjectivesPanel({
  objectives,
}: {
  objectives: Array<{ description: string; workflow_id?: string; status?: string }>;
}) {
  if (!objectives.length) {
    return <p className="text-odin-muted text-sm">No active objectives linked to this session.</p>;
  }
  return (
    <ul className="space-y-2 text-sm">
      {objectives.map((o, i) => (
        <li key={i} className="rounded-lg border border-odin-border bg-odin-panel px-4 py-3">
          <p>{o.description}</p>
          {o.workflow_id && (
            <p className="text-xs text-odin-muted mt-1 font-mono">wf: {o.workflow_id.slice(0, 12)}…</p>
          )}
        </li>
      ))}
    </ul>
  );
}
