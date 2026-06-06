"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Project Memory"
      subtitle="Persistent project cognition"
      endpoint="/runtime/project-memory"
      rootKey="project_memory"
      description="Engineering timeline, decisions, architecture memory, and instant resume."
    />
  );
}
