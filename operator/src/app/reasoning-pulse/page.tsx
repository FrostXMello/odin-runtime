"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Reasoning Pulse" subtitle="Live cognition" endpoint="/runtime/reasoning-pulse" rootKey="cognitive_streams" description="Live reasoning pulse with adaptive FPS scaling." />;
}
