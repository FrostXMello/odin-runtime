"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Objectives" subtitle="Active objective trees" endpoint="/runtime/objectives/active" rootKey="objective_management" description="Persistent objective registry with milestone tracking and stalled detection." />;
}
