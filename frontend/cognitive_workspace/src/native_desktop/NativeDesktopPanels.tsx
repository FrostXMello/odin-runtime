export function FloatingOverlaySystem({ overlays }: { overlays: string[] }) {
  return (
    <div className="floating-overlay-system">
      {overlays.map((o) => (
        <div key={o} className="floating-overlay">
          {o}
        </div>
      ))}
    </div>
  );
}

export function DesktopCognitionPulse({ active }: { active: boolean }) {
  return <div className={`desktop-cognition-pulse ${active ? "active" : ""}`} />;
}

export function WorkspaceOrbitMapV2({ nodes }: { nodes: string[] }) {
  return (
    <div className="workspace-orbit-map-v2">
      {nodes.map((n) => (
        <span key={n}>{n}</span>
      ))}
    </div>
  );
}

export function LiveWindowGraph({ windows }: { windows: string[] }) {
  return (
    <ul className="live-window-graph">
      {windows.map((w) => (
        <li key={w}>{w}</li>
      ))}
    </ul>
  );
}

export function InterruptionPressureRadar({ levels }: { levels: number[] }) {
  return (
    <div className="interruption-pressure-radar">
      {levels.map((l, i) => (
        <div key={i} style={{ opacity: l / 100 }} className="pressure-blip" />
      ))}
    </div>
  );
}

export function FocusSurface({ minutes }: { minutes: number }) {
  return <div className="focus-surface" data-minutes={minutes} />;
}

export function WorkspaceContinuityTimeline({ events }: { events: string[] }) {
  return (
    <ol className="workspace-continuity-timeline">
      {events.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ol>
  );
}

export function ResumeChainViewer({ chain }: { chain: string[] }) {
  return (
    <ol className="resume-chain-viewer">
      {chain.map((step) => (
        <li key={step}>{step}</li>
      ))}
    </ol>
  );
}

export function AdaptiveOverlayShell({ mode }: { mode: string }) {
  return <div className="adaptive-overlay-shell" data-mode={mode} />;
}
