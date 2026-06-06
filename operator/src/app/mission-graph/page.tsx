"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Mission Graph" subtitle="Dependency graph" endpoint="/runtime/mission-graph" rootKey="mission_graph" description="Persistent mission dependency graph with continuity scoring." />;
}
