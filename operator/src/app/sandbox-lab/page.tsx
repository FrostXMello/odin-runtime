"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Sandbox Lab"
      subtitle="Isolated experiments"
      endpoint="/runtime/self-improvement-sandbox"
      rootKey="self_improvement_sandbox"
      description="Branch lab, patch simulation, rollback rehearsal — no production deploy."
    />
  );
}
