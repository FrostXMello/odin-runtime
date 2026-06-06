"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Focus Heatmap" subtitle="Attention map" endpoint="/runtime/focus-heatmap" rootKey="attention_engine" description="Live focus heatmap with cognitive pressure estimation." />;
}
