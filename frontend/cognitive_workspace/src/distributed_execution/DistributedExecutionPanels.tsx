export function ExecutionDagRenderer({ nodes }: { nodes: string[] }) {
  return (
    <div className="execution-dag-renderer">
      {nodes.map((n) => (
        <span key={n} className="dag-node">{n}</span>
      ))}
    </div>
  );
}

export function RollbackGraphViewer({ steps }: { steps: string[] }) {
  return (
    <ol className="rollback-graph-viewer">
      {steps.map((s) => (
        <li key={s}>{s}</li>
      ))}
    </ol>
  );
}

export function DistributedExecutionRadar({ health }: { health: number }) {
  return <div className="distributed-execution-radar" data-health={health} />;
}

export function WorkspaceFederationMap({ workspaces }: { workspaces: string[] }) {
  return (
    <ul className="workspace-federation-map">
      {workspaces.map((w) => (
        <li key={w}>{w}</li>
      ))}
    </ul>
  );
}

export function InterventionForecastSurface({ risk }: { risk: number }) {
  return <div className="intervention-forecast-surface" data-risk={risk} />;
}

export function WorkflowStabilizationMonitor({ stable }: { stable: boolean }) {
  return <div className="workflow-stabilization-monitor" data-stable={stable} />;
}

export function ExecutionResilienceHeatmap({ score }: { score: number }) {
  return <div className="execution-resilience-heatmap" data-score={score} />;
}

export function PredictiveRecoverySimulator({ path }: { path: string[] }) {
  return (
    <ol className="predictive-recovery-simulator">
      {path.map((p) => (
        <li key={p}>{p}</li>
      ))}
    </ol>
  );
}
