"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Failure Lineage"
      subtitle="Failure-chain tracing"
      endpoint="/runtime/failure-lineage"
      rootKey="causality_mapping"
      description="Trace failure chains across runtimes with supervised causality reconstruction."
    />
  );
}
