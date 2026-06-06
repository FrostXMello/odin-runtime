"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Live Orchestration" subtitle="Real-time orchestration" endpoint="/runtime/live-orchestration" rootKey="live_orchestration" description="Live runtime orchestration visibility with cognition pulse and health scoring." />;
}
