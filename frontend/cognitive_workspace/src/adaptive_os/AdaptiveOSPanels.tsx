export function AdaptiveCognitionHUD({ load, profile }: { load: number; profile: string }) {
  return (
    <header className="adaptive-hud">
      <span>{profile}</span>
      <span>Load {(load * 100).toFixed(0)}%</span>
    </header>
  );
}

export function AttentionFieldV2() {
  return <div className="attention-field-v2" />;
}

export function CognitiveLoadHeatmap({ cells }: { cells: number[] }) {
  return (
    <div className="cognitive-load-heatmap">
      {cells.map((c, i) => (
        <div key={i} style={{ opacity: c / 100 }} className="cell" />
      ))}
    </div>
  );
}

export function ReasoningRiverV2({ tokens }: { tokens: string[] }) {
  return (
    <div className="reasoning-river-v2">
      {tokens.map((t, i) => (
        <span key={i}>{t}</span>
      ))}
    </div>
  );
}

export function WorkspaceTimeline({ events }: { events: string[] }) {
  return (
    <ol className="workspace-timeline">
      {events.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ol>
  );
}

export function UpgradeProposalCenter({ proposals }: { proposals: string[] }) {
  return (
    <ul className="upgrade-proposals">
      {proposals.map((p) => (
        <li key={p}>{p} — approval required</li>
      ))}
    </ul>
  );
}

export function MemoryFabricExplorer({ nodes }: { nodes: string[] }) {
  return (
    <div className="memory-fabric-explorer">
      {nodes.map((n) => (
        <span key={n}>{n}</span>
      ))}
    </div>
  );
}

export function EvolutionDashboard({ metrics }: { metrics: Record<string, number> }) {
  return (
    <dl className="evolution-dashboard">
      {Object.entries(metrics).map(([k, v]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd>{v}</dd>
        </div>
      ))}
    </dl>
  );
}
