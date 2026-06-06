type Node = { id: string; label: string };
type Edge = { from: string; to: string };

export function ReasoningGraph({ nodes, edges }: { nodes: Node[]; edges: Edge[] }) {
  return (
    <div className="reasoning-graph">
      <svg viewBox="0 0 400 200">
        {edges.map((e, i) => (
          <line key={i} x1={40 + i * 30} y1="40" x2={120 + i * 30} y2="120" stroke="#4fd1c5" />
        ))}
        {nodes.map((n, i) => (
          <g key={n.id} transform={`translate(${20 + i * 60}, ${i % 2 ? 130 : 20})`}>
            <circle r="12" fill="#6366f1" />
            <text y="28" fontSize="10" fill="#cbd5e1">
              {n.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
