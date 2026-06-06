"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Replay Orchestration"
      subtitle="Bounded cognition playback"
      endpoint="/runtime/replay-orchestration"
      rootKey="replay_orchestration"
      description="Replay coordination, checkpoint routing, and continuity replay windows."
    />
  );
}
