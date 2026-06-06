"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Long Horizon Planning" subtitle="Deferred planning" endpoint="/runtime/autonomous-loop-v2" rootKey="autonomous_loop_v2" description="Bounded long-horizon engineering coordination." />;
}
