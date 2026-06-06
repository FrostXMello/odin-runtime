"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Workspace Coordination" subtitle="Multi-workspace" endpoint="/runtime/workspace-coordination" rootKey="workspace_coordination" description="Simultaneous workspace continuity and cross-project linking." />;
}
