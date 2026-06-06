"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Autonomous Workspace" subtitle="Session continuity" endpoint="/runtime/autonomous-workspace" rootKey="autonomous_workspace" description="Persistent session graph, workflow recovery, and cross-project continuity." />;
}
