export function CognitionHeartbeatRiver({ beats }: { beats: number[] }) {
  return (
    <div className="cognition-heartbeat-river">
      {beats.map((b, i) => (
        <span key={i} style={{ opacity: b / 100 }} />
      ))}
    </div>
  );
}

export function AttentionFieldUnified({ cells }: { cells: number[] }) {
  return (
    <div className="attention-field-unified">
      {cells.map((c, i) => (
        <div key={i} style={{ opacity: c }} className="attention-cell" />
      ))}
    </div>
  );
}

export function RuntimeSynchronizationMap({ nodes }: { nodes: string[] }) {
  return (
    <div className="runtime-sync-map">
      {nodes.map((n) => (
        <span key={n} className="sync-node">
          {n}
        </span>
      ))}
    </div>
  );
}

export function PersistentAgentConstellation({ agents }: { agents: string[] }) {
  return (
    <div className="persistent-agent-constellation">
      {agents.map((a) => (
        <span key={a} className="agent-node">
          {a}
        </span>
      ))}
    </div>
  );
}

export function ActiveObjectiveStack({ objectives }: { objectives: string[] }) {
  return (
    <ol className="active-objective-stack">
      {objectives.map((o) => (
        <li key={o}>{o}</li>
      ))}
    </ol>
  );
}

export function DeferredCognitionQueue({ tasks }: { tasks: string[] }) {
  return (
    <ul className="deferred-cognition-queue">
      {tasks.map((t) => (
        <li key={t}>{t}</li>
      ))}
    </ul>
  );
}

export function CognitivePressureMeter({ pressure }: { pressure: number }) {
  return (
    <div className="cognitive-pressure-meter" data-pressure={pressure}>
      {(pressure * 100).toFixed(0)}%
    </div>
  );
}

export function UnifiedCoreModeShell({ mode }: { mode: string }) {
  return <div className="unified-core-mode" data-mode={mode} />;
}
