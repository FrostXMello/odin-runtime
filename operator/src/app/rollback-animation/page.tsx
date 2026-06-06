"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Rollback Animation Engine"
      subtitle="Live rollback DAG animation"
      endpoint="/runtime/rollback-animation/graph"
      rootKey="rollback_animation_engine"
      description="Animated rollback transitions, execution chain playback, and bounded replay synchronization."
    />
  );
}
