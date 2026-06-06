"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return (
    <DesktopExperiencePanel title="Cognitive Streams" subtitle="Live thought streams" endpoint="/runtime/cognitive-streams" rootKey="cognitive_streams" description="Continuous cognition streams with adaptive compression and low-resource fallback." />
  );
}
