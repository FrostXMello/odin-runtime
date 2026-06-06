"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Rollback DAG Live"
      subtitle="Real-time DAG renderer"
      endpoint="/runtime/rollback-dag-live"
      rootKey="rollback_animation_engine"
      description="Live rollback DAG animation with virtualization and convergence visualization."
    />
  );
}
