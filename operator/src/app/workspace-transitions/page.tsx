"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Workspace Transitions" subtitle="Transition timeline" endpoint="/runtime/window-awareness/workspace" rootKey="window_awareness" description="Workspace transition detection and semantic tagging." />;
}
