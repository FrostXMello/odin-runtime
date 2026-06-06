"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Runtime Dependencies"
      subtitle="Cross-runtime dependency mapping"
      endpoint="/runtime/runtime-dependencies"
      rootKey="causality_mapping"
      description="Map runtime dependencies and reconstruct reasoning paths across missions."
    />
  );
}
