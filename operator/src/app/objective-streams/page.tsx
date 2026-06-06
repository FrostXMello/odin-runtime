"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Objective Streams" subtitle="Live objective flow" endpoint="/runtime/objective-streams" rootKey="objective_streams" description="Continuous objective progression with adaptive reprioritization." />;
}
