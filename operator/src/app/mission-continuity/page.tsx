"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Mission Continuity" subtitle="Workflow recovery" endpoint="/runtime/mission-continuity/resume-chain" rootKey="mission_continuity" description="Interrupted workflow resurfacing and mission resume chains." />;
}
