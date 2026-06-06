"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Live Cognition Timeline" subtitle="Unified cognition playback" endpoint="/runtime/live-cognition-timeline" rootKey="live_cognition_timeline" description="Mission timeline rendering with execution and governance chronology." />;
}
