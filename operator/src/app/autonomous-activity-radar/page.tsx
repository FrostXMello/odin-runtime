"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Activity Radar" subtitle="Live radar" endpoint="/runtime/autonomous-activity/radar" rootKey="realtime_cognition" description="Live autonomous activity radar across cognitive infrastructure." />;
}
