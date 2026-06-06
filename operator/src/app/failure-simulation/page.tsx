"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Failure Simulation" subtitle="Chain simulator" endpoint="/runtime/failure-simulation" rootKey="cognitive_risk" description="Failure chain simulation with bounded risk loops." />;
}
