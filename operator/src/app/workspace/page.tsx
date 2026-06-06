"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Cognitive Workspace"
      subtitle="Unified operating surface"
      endpoint="/runtime/cognitive-workspace"
      rootKey="cognitive_workspace"
      description="Adaptive workspace with draggable panels, mission dock, live memory timeline, and voice dock."
    />
  );
}
