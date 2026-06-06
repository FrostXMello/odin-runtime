"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Autonomous Loop V2" subtitle="Persistent agent loop" endpoint="/runtime/autonomous-loop-v2" rootKey="autonomous_loop_v2" description="Multi-day task continuity with approval-gated execution." />;
}
