"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cross Workspace" subtitle="Multi-project map" endpoint="/runtime/cross-workspace/map" rootKey="cross_workspace_coordination" description="Multi-project coordination with workspace dependency awareness." />;
}
