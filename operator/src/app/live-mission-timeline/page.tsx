"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Live Mission Timeline" subtitle="Mission continuity" endpoint="/runtime/live-mission-timeline" rootKey="mission_graph" description="Long-horizon mission timeline with graph continuity scoring." />;
}
