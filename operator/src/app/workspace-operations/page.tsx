"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Workspace Operations" subtitle="Operational state" endpoint="/runtime/workspace-operations/state" rootKey="workspace_operations" description="Live workspace operational state with recovery and correlation." />;
}
