export function NativeDesktopShell({ mode }: { mode: string }) {
  return (
    <div className="native-desktop-shell" data-mode={mode}>
      <aside className="persistent-dock">Odin</aside>
      <main className="desktop-main" />
    </div>
  );
}

export function ReasoningPulse({ active }: { active: boolean }) {
  return <div className={`reasoning-pulse ${active ? "active" : ""}`} />;
}

export function AgentConstellation({ agents }: { agents: string[] }) {
  return (
    <div className="agent-constellation">
      {agents.map((a) => (
        <span key={a} className="agent-node">
          {a}
        </span>
      ))}
    </div>
  );
}

export function WorkspaceOrbitMap({ orbits }: { orbits: number[] }) {
  return (
    <div className="workspace-orbit-map">
      {orbits.map((o, i) => (
        <div key={i} className="orbit" style={{ opacity: o / 100 }} />
      ))}
    </div>
  );
}

export function MissionTimelineRiver({ events }: { events: string[] }) {
  return (
    <ol className="mission-timeline-river">
      {events.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ol>
  );
}

export function AutonomousActivityStream({ items }: { items: string[] }) {
  return (
    <ul className="autonomous-activity-stream">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function AdaptiveSidebar({ collapsed }: { collapsed: boolean }) {
  return <nav className={`adaptive-sidebar ${collapsed ? "collapsed" : ""}`} />;
}

export function FloatingCopilot({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return <div className="floating-copilot">Copilot</div>;
}

export function CinematicCognitionMode({ enabled, fpsCap }: { enabled: boolean; fpsCap: number }) {
  return (
    <div className="cinematic-cognition" data-enabled={enabled} data-fps-cap={fpsCap}>
      Cinematic
    </div>
  );
}

export function LowPowerRenderingMode({ enabled }: { enabled: boolean }) {
  return <div className="low-power-render" data-enabled={enabled} />;
}
