"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cog Maintenance" subtitle="Compaction" endpoint="/runtime/cognitive-maintenance" rootKey="cognitive_maintenance" description="Memory consolidation, stream compression, and runtime stabilization." />;
}
