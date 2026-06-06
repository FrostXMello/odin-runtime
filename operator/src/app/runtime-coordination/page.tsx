"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Coord" subtitle="Sync layer" endpoint="/runtime/runtime-coordination" rootKey="runtime_coordination" description="Detect overlaps, merge contexts, and resolve priority conflicts." />;
}
