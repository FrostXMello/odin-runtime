"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cognitive State" subtitle="Global state" endpoint="/runtime/cognitive-state" rootKey="cognitive_state" description="Cognitive pressure, operator engagement, and runtime load." />;
}
