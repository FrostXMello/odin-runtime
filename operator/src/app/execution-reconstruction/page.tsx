"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Execution Reconstruction"
      subtitle="Bounded replay restoration"
      endpoint="/runtime/execution-reconstruction"
      rootKey="execution_reconstruction"
      description="Reconstruct execution states, rebuild workspace sequences, and restore cognition windows."
    />
  );
}
