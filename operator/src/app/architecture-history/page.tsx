"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Architecture History"
      subtitle="Project memory timeline"
      endpoint="/runtime/project-memory"
      rootKey="project_memory"
      description="Architecture evolution memory and engineering timeline replay."
    />
  );
}
