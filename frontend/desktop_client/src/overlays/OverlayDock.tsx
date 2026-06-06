const KINDS = ["terminal", "debug", "mission_hud", "subtitles", "memory_hint", "workflow"] as const;

export type OverlayKind = (typeof KINDS)[number];

export function OverlayDock({ attached }: { attached: OverlayKind[] }) {
  return (
    <aside className="overlay-dock">
      {KINDS.map((k) => (
        <span key={k} className={attached.includes(k) ? "on" : ""}>
          {k}
        </span>
      ))}
    </aside>
  );
}
