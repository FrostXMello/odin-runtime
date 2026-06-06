"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return (
    <DesktopExperiencePanel title="Memory Fabric" subtitle="Unified memory graph" endpoint="/runtime/memory-fabric" rootKey="memory_fabric" description="Cross-runtime memory linking, temporal replay, and rehydration after restart." />
  );
}
