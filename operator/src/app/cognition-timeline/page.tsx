"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Cognition Timeline"
      subtitle="Cognition replay river"
      endpoint="/runtime/cognition-timeline"
      rootKey="timeline_visualization"
      description="Cinematic cognition replay with continuity overlays and timeline navigation."
    />
  );
}
