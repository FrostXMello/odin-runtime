"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Engineering Council"
      subtitle="Collaborative agents"
      endpoint="/runtime/engineering-society"
      rootKey="engineering_society"
      description="Supervised architecture debate, role assignment, and review consensus."
    />
  );
}
