"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return (
    <DesktopExperiencePanel title="Cognitive Kernel" subtitle="Central orchestration" endpoint="/runtime/cognitive-kernel" rootKey="cognitive_kernel" description="Persistent cognitive kernel — attention routing, continuity, and heartbeat scheduling." />
  );
}
