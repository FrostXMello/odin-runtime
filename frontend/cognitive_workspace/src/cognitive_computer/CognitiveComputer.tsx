export function CognitionHUD({ tick, familiarity }: { tick: number; familiarity: number }) {
  return (
    <header className="cognition-hud">
      <span>Kernel tick {tick}</span>
      <span>Familiarity {(familiarity * 100).toFixed(0)}%</span>
    </header>
  );
}

export function MemoryField({ nodes }: { nodes: string[] }) {
  return (
    <div className="memory-field">
      {nodes.map((n) => (
        <span key={n} className="memory-node">{n}</span>
      ))}
    </div>
  );
}

export function ReasoningRiver({ tokens }: { tokens: string[] }) {
  return (
    <div className="reasoning-river">
      {tokens.map((t, i) => (
        <span key={i} className="token">{t}</span>
      ))}
    </div>
  );
}

export function AttentionSurface() {
  return <div className="attention-surface" aria-label="attention surface" />;
}

export function ContinuityTimeline({ events }: { events: string[] }) {
  return (
    <ol className="continuity-timeline">
      {events.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ol>
  );
}

export function EnvironmentMap({ zones }: { zones: string[] }) {
  return (
    <div className="environment-map">
      {zones.map((z) => (
        <div key={z} className="zone">{z}</div>
      ))}
    </div>
  );
}

export function CognitionPulse() {
  return <div className="cognition-pulse" />;
}
