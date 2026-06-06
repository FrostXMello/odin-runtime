export function ReasoningGraph({ nodes }: { nodes: string[] }) {
  return (
    <svg className="reasoning-graph" viewBox="0 0 300 120">
      {nodes.map((n, i) => (
        <g key={n} transform={`translate(${20 + i * 70}, ${i % 2 ? 70 : 20})`}>
          <circle r="14" fill="#818cf8" />
          <text y="28" fontSize="10" fill="#e2e8f0">{n}</text>
        </g>
      ))}
    </svg>
  );
}
