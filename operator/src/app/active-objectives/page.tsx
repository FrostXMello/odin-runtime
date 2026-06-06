"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Objectives" subtitle="Active stack" endpoint="/runtime/active-objectives" rootKey="unified_cognitive_core" description="Active objective stack and task continuity." />;
}
