/**
 * Live desktop context collector — opt-in, posts to ODIN backend.
 * Collects what Electron can observe without unrestricted OS control.
 */

const API_BASE = process.env.ODIN_API_URL ?? "http://127.0.0.1:8000/api/v1";

export interface DesktopSnapshot {
  active_app?: string;
  active_window?: { title: string; id?: string };
  project?: string;
  vscode?: { workspace?: string; open_files?: string[] };
  browser_tabs?: Array<{ url: string; title: string }>;
  terminals?: Array<{ cwd?: string; output_preview?: string }>;
  clipboard_preview?: string;
  monitors?: number;
  platform: string;
  collected_at: string;
  collector: string;
}

let collectorEnabled = false;
let intervalId: ReturnType<typeof setInterval> | null = null;

export function setCollectorEnabled(enabled: boolean): void {
  collectorEnabled = enabled;
  if (!enabled && intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}

export function isCollectorEnabled(): boolean {
  return collectorEnabled;
}

export async function collectSnapshot(
  extras?: Partial<DesktopSnapshot>
): Promise<DesktopSnapshot> {
  const { app, BrowserWindow } = await import("electron");
  const win = BrowserWindow.getFocusedWindow();
  const title = win?.getTitle() ?? "ODIN Command Center";

  const snapshot: DesktopSnapshot = {
    active_app: app.getName(),
    active_window: { title },
    project: "PROJECT_ODIN",
    platform: process.platform,
    collected_at: new Date().toISOString(),
    collector: "electron_bridge",
    monitors: 1,
    ...extras,
  };
  return snapshot;
}

export async function publishSnapshot(snapshot: DesktopSnapshot): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/desktop-runtime/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(snapshot),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export function startCollector(intervalMs = 5000, onTick?: (ok: boolean) => void): void {
  if (intervalId) clearInterval(intervalId);
  collectorEnabled = true;
  intervalId = setInterval(async () => {
    if (!collectorEnabled) return;
    const snap = await collectSnapshot();
    const ok = await publishSnapshot(snap);
    onTick?.(ok);
  }, intervalMs);
}

export function stopCollector(): void {
  setCollectorEnabled(false);
}
