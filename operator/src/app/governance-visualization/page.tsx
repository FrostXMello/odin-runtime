"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Governance Visualization" subtitle="Governance HUD" endpoint="/runtime/governance-visualization" rootKey="governance_visualization" description="Governance cinematic HUD with risk heatmaps and confidence layers." />;
}
