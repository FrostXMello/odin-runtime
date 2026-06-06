export function ObjectiveGraphViewer({ nodes }: { nodes: string[] }) {
  return (
    <div className="objective-graph-viewer">
      {nodes.map((n) => (
        <span key={n} className="objective-node">{n}</span>
      ))}
    </div>
  );
}

export function RuntimeCoordinationMap({ runtimes }: { runtimes: string[] }) {
  return (
    <ul className="runtime-coordination-map">
      {runtimes.map((r) => (
        <li key={r}>{r}</li>
      ))}
    </ul>
  );
}

export function ContinuityHealthTimeline({ scores }: { scores: number[] }) {
  return (
    <div className="continuity-health-timeline">
      {scores.map((s, i) => (
        <div key={i} className="health-point" style={{ opacity: s }} />
      ))}
    </div>
  );
}

export function ReasoningBudgetRiver({ budget }: { budget: number }) {
  return <div className="reasoning-budget-river" data-budget={budget} />;
}

export function MissionDependencyTree({ deps }: { deps: string[] }) {
  return (
    <ol className="mission-dependency-tree">
      {deps.map((d) => (
        <li key={d}>{d}</li>
      ))}
    </ol>
  );
}

export function AdaptivePlanningSurface({ mode }: { mode: string }) {
  return <div className="adaptive-planning-surface" data-mode={mode} />;
}

export function OperatorAlignmentDashboard({ alignment }: { alignment: number }) {
  return <div className="operator-alignment-dashboard" data-alignment={alignment} />;
}

export function CognitiveSynchronizationPulse({ active }: { active: boolean }) {
  return <div className={`cognitive-sync-pulse ${active ? "active" : ""}`} />;
}
