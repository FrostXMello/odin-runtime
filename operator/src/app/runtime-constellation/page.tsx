"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Constellation" subtitle="Runtime map" endpoint="/runtime/runtime-constellation" rootKey="cognitive_visual_layers" description="Cinematic runtime constellation with lazy visual hydration." />;
}
