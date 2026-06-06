import type { WorkspaceMode } from "./modes";

const MODES: WorkspaceMode[] = ["minimal", "operator", "engineering", "immersive", "cinematic"];

type Props = { mode: WorkspaceMode; onMode: (m: WorkspaceMode) => void };

export function AdaptiveShell({ mode, onMode }: Props) {
  return (
    <header className="adaptive-shell">
      <strong>Cognitive Workspace</strong>
      <nav>
        {MODES.map((m) => (
          <button key={m} className={mode === m ? "active" : ""} onClick={() => onMode(m)}>
            {m}
          </button>
        ))}
      </nav>
    </header>
  );
}
