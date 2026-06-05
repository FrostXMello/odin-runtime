export function AgentSocietyMonitor({
  agents,
}: {
  agents: Array<{ agent_id: string; domains: string[]; reliability_score: number }>;
}) {
  return (
    <table className="w-full max-w-2xl text-sm">
      <thead>
        <tr className="text-odin-muted text-left border-b border-odin-border">
          <th className="py-2">Agent</th>
          <th>Domains</th>
          <th>Reliability</th>
        </tr>
      </thead>
      <tbody>
        {agents.map((a) => (
          <tr key={a.agent_id} className="border-b border-odin-border/50">
            <td className="py-2 font-mono text-odin-accent">{a.agent_id}</td>
            <td>{a.domains.join(", ")}</td>
            <td>{(a.reliability_score * 100).toFixed(0)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
