export function ExecutionIntelligenceDashboard({
  scores,
}: {
  scores: Array<{ tool_name: string; success_rate: number; sample_size: number }>;
}) {
  if (!scores.length) {
    return <p className="text-odin-muted text-sm">No tool reliability data yet.</p>;
  }
  return (
    <table className="w-full max-w-lg text-sm">
      <thead>
        <tr className="text-odin-muted text-left border-b border-odin-border">
          <th className="py-2">Tool</th>
          <th>Success</th>
          <th>Samples</th>
        </tr>
      </thead>
      <tbody>
        {scores.map((s) => (
          <tr key={s.tool_name} className="border-b border-odin-border/50">
            <td className="py-2 font-mono text-odin-accent">{s.tool_name}</td>
            <td>{(s.success_rate * 100).toFixed(0)}%</td>
            <td>{s.sample_size}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
