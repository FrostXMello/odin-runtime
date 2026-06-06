"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Operator Experience"
      subtitle="Daily driver runtime"
      endpoint="/runtime/operator-experience"
      rootKey="operator_experience"
      description="Startup resume, morning briefing, focus shifts, and workspace rehydration."
    />
  );
}
