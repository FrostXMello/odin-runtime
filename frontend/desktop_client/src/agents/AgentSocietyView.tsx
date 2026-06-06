export function AgentSocietyView({ agents }: { agents: string[] }) {
  return (
    <div className="agent-society">
      {agents.map((a) => (
        <div key={a} className="agent-node">
          {a}
        </div>
      ))}
    </div>
  );
}
