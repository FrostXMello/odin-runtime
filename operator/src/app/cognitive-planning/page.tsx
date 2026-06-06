"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cognitive Planning" subtitle="Adaptive planning" endpoint="/runtime/cognitive-planning/budget" rootKey="cognitive_planning" description="Focus-aware cognitive planning with reasoning budget allocation." />;
}
