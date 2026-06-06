"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Realtime Coordination" subtitle="Stream multiplexing" endpoint="/runtime/realtime-coordination" rootKey="realtime_coordination" description="Live runtime balancing with bounded stream multiplexing." />;
}
