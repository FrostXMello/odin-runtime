"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Context Rehydration" subtitle="Session restore" endpoint="/runtime/memory-fabric-v2" rootKey="memory_fabric_v2" description="Replayable engineering sessions and context resurrection." />;
}
