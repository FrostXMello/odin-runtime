"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Live Visualization"
      subtitle="Reasoning + society graphs"
      endpoint="/runtime/live-visualization"
      rootKey="live_visualization"
      description="Live reasoning DAG, memory activation, mission waves, and agent collaboration."
    />
  );
}
