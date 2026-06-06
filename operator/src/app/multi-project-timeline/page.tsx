"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Multi-Project Timeline" subtitle="Unified sessions" endpoint="/runtime/workspace-coordination" rootKey="workspace_coordination" description="Unified project timelines and engineering session coordination." />;
}
