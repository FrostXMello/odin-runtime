"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Live Overlays V2" subtitle="Floating cognitive HUD" endpoint="/runtime/live-overlays-v2" rootKey="live_overlays_v2" description="Adaptive overlay system with focus-aware suppression and throttling." />;
}
