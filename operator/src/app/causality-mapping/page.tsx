"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Causality Mapping"
      subtitle="Causal execution graphing"
      endpoint="/runtime/causality-mapping/graph"
      rootKey="causality_mapping"
      description="Causal execution graphs, failure-chain linkage, and operator-visible reasoning lineage."
    />
  );
}
