import type { DesktopMode } from "../shell/modes";

type Props = { mode: DesktopMode; onMode: (m: DesktopMode) => void };

const MODES: DesktopMode[] = ["compact", "balanced", "immersive", "cinematic"];

export function ShellBar({ mode, onMode }: Props) {
  return (
    <header className="shell-bar">
      <strong>Odin Desktop</strong>
      <nav>
        {MODES.map((m) => (
          <button key={m} className={m === mode ? "active" : ""} onClick={() => onMode(m)}>
            {m}
          </button>
        ))}
      </nav>
    </header>
  );
}
