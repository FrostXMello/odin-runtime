"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Autonomous Activity" subtitle="Live activity" endpoint="/runtime/autonomous-activity" rootKey="autonomous_loop_v2" description="Live autonomous activity stream across runtimes." />;
}
