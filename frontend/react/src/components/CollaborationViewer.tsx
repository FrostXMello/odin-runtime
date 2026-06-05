export function CollaborationViewer({
  chains,
}: {
  chains: Array<{ id: string; objective: string; steps: Array<{ agent: string; description: string }> }>;
}) {
  if (!chains.length) {
    return <p className="text-odin-muted text-sm">No collaboration chains.</p>;
  }
  return (
    <ul className="space-y-4">
      {chains.map((c) => (
        <li key={c.id} className="rounded-lg border border-odin-border p-4">
          <p className="font-medium">{c.objective}</p>
          <ol className="mt-2 space-y-1 text-sm text-odin-muted list-decimal pl-5">
            {c.steps.map((s, i) => (
              <li key={i}>
                <span className="text-odin-accent font-mono">{s.agent}</span> — {s.description}
              </li>
            ))}
          </ol>
        </li>
      ))}
    </ul>
  );
}
