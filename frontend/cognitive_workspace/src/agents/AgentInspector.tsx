export function AgentInspector({ agents }: { agents: string[] }) {
  return (
    <div className="agent-inspector">
      {agents.map((a) => (
        <div key={a} className="agent-card">{a}</div>
      ))}
    </div>
  );
}
