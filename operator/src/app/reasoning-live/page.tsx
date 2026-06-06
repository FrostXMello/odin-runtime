"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Reasoning Live"
      subtitle="Token streaming surface"
      endpoint="/runtime/reasoning-live"
      rootKey="live_reasoning"
      description="Live reasoning branches, confidence heatmaps, memory recalls, and mission cognition playback."
    />
  );
}
