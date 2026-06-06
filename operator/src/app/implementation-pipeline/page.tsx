"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Implementation Pipeline"
      subtitle="Workflow stages"
      endpoint="/runtime/engineering-workflows"
      rootKey="engineering_workflows_v2"
      description="Goal pipeline, milestones, staged implementation, and sprint continuity."
    />
  );
}
