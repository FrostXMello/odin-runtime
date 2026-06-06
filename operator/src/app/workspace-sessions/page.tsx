"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Workspace Sessions" subtitle="Persistent session registry" endpoint="/runtime/workspace-sessions" rootKey="workspace_sessions" description="SQLite-backed workspace session snapshots and restore chains." />;
}
