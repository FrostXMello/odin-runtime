"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Workspace Federation" subtitle="Federation map" endpoint="/runtime/workspace-federation" rootKey="cross_workspace_coordination" description="Workspace federation with bounded sync loops and recovery." />;
}
