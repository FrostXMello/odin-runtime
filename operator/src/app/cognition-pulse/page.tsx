"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cognition Pulse" subtitle="Live pulse" endpoint="/runtime/cognition-pulse" rootKey="live_orchestration" description="Real-time cognition pulse with orchestration continuity." />;
}
