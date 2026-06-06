export function RealtimeCognitionRiver({ tokens }: { tokens: string[] }) {
  return (
    <div className="realtime-cognition-river">
      {tokens.map((t, i) => (
        <span key={i}>{t}</span>
      ))}
    </div>
  );
}

export function WorkspaceConstellationMap({ nodes }: { nodes: string[] }) {
  return (
    <div className="workspace-constellation">
      {nodes.map((n) => (
        <span key={n} className="constellation-node">
          {n}
        </span>
      ))}
    </div>
  );
}

export function AutonomousActivityRadar({ signals }: { signals: number[] }) {
  return (
    <div className="autonomous-activity-radar">
      {signals.map((s, i) => (
        <div key={i} style={{ opacity: s / 100 }} className="radar-blip" />
      ))}
    </div>
  );
}

export function LongHorizonTimeline({ events }: { events: string[] }) {
  return (
    <ol className="long-horizon-timeline">
      {events.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ol>
  );
}

export function PredictiveMemorySurface({ topics }: { topics: string[] }) {
  return (
    <ul className="predictive-memory-surface">
      {topics.map((t) => (
        <li key={t}>{t}</li>
      ))}
    </ul>
  );
}

export function EngineeringReliabilityGraph({ metrics }: { metrics: Record<string, number> }) {
  return (
    <dl className="engineering-reliability-graph">
      {Object.entries(metrics).map(([k, v]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd>{v}</dd>
        </div>
      ))}
    </dl>
  );
}

export function AdaptiveCognitionPulse({ active, fpsCap }: { active: boolean; fpsCap: number }) {
  return <div className={`cognition-pulse ${active ? "active" : ""}`} data-fps-cap={fpsCap} />;
}

export function OperatorHealthDashboard({ health }: { health: Record<string, boolean> }) {
  return (
    <dl className="operator-health-dashboard">
      {Object.entries(health).map(([k, v]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd>{v ? "ok" : "attention"}</dd>
        </div>
      ))}
    </dl>
  );
}

export function ContinuousReasoningOverlay({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return <div className="continuous-reasoning-overlay" />;
}

export function PredictiveAttentionMap({ cells }: { cells: number[] }) {
  return (
    <div className="predictive-attention-map">
      {cells.map((c, i) => (
        <div key={i} style={{ opacity: c / 100 }} className="attention-cell" />
      ))}
    </div>
  );
}

export function LowPowerOvernightRender({ enabled }: { enabled: boolean }) {
  return <div className="low-power-overnight" data-enabled={enabled} />;
}
