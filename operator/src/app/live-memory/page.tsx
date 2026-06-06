"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Live Memory"
      subtitle="Memory surface"
      endpoint="/runtime/desktop-overlay/memory-surface"
      description="Memory thread explorer and activation graph for the cognitive desktop."
    />
  );
}
