export function MissionMap({ nodes }: { nodes: string[] }) {
  return (
    <div className="mission-map">
      {nodes.map((n) => (
        <div key={n} className="pulse">{n}</div>
      ))}
    </div>
  );
}

export function AgentConstellation({ agents }: { agents: string[] }) {
  return (
    <div className="agent-constellation">
      {agents.map((a) => (
        <span key={a} className="star">{a}</span>
      ))}
    </div>
  );
}

export function MemoryPulse() {
  return <div className="memory-pulse" aria-label="memory pulse" />;
}

export function AttentionField() {
  return <div className="attention-field" />;
}

export function VoiceReactiveOverlay({ level }: { level: number }) {
  return <div className="voice-overlay" style={{ opacity: level }} />;
}
