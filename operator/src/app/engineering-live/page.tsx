"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Engineering Live"
      subtitle="Live orchestrator"
      endpoint="/runtime/live-engineering"
      rootKey="live_engineering_orchestrator"
      description="Continuous engineering session tracking, repo attention, and proactive debugging."
    />
  );
}
