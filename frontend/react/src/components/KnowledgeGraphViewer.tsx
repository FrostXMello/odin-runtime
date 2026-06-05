export function KnowledgeGraphViewer({
  nodes,
}: {
  nodes: Array<Record<string, unknown>>;
}) {
  if (!nodes.length) {
    return <p className="text-odin-muted text-sm">No graph matches.</p>;
  }
  return (
    <ul className="space-y-2 font-mono text-xs">
      {nodes.map((n, i) => (
        <li key={i} className="rounded border border-odin-border px-3 py-2">
          <span className="text-odin-accent">{String(n.entity ?? "")}</span>
          <span className="text-odin-muted ml-2">{String(n.type ?? "")}</span>
        </li>
      ))}
    </ul>
  );
}
