"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Memory Fabric V2" subtitle="Semantic memory" endpoint="/runtime/memory-fabric-v2" rootKey="memory_fabric_v2" description="Persistent semantic memory and cross-session linkage." />;
}
