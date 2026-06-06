export function OvernightCognitionRiver({ cycles }: { cycles: number[] }) {
  return (
    <div className="overnight-cognition-river">
      {cycles.map((c, i) => (
        <span key={i} style={{ opacity: c / 100 }} />
      ))}
    </div>
  );
}

export function DeferredReasoningGraph({ nodes }: { nodes: string[] }) {
  return (
    <div className="deferred-reasoning-graph">
      {nodes.map((n) => (
        <span key={n} className="reasoning-node">
          {n}
        </span>
      ))}
    </div>
  );
}

export function AbandonedWorkflowMap({ items }: { items: string[] }) {
  return (
    <ul className="abandoned-workflow-map">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function MorningBriefingSurface({ sections }: { sections: string[] }) {
  return (
    <article className="morning-briefing-surface">
      {sections.map((s) => (
        <section key={s}>{s}</section>
      ))}
    </article>
  );
}

export function RepoDriftRadar({ signals }: { signals: number[] }) {
  return (
    <div className="repo-drift-radar">
      {signals.map((s, i) => (
        <div key={i} style={{ opacity: s / 100 }} className="drift-blip" />
      ))}
    </div>
  );
}

export function OvernightEngineeringTimeline({ events }: { events: string[] }) {
  return (
    <ol className="overnight-engineering-timeline">
      {events.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ol>
  );
}

export function CognitionRecoveryStream({ items }: { items: string[] }) {
  return (
    <ul className="cognition-recovery-stream">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function LowPowerOvernightShell({ mode }: { mode: string }) {
  return <div className="low-power-overnight-shell" data-mode={mode} />;
}
