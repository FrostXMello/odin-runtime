"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Realtime Cognition" subtitle="Live heartbeat" endpoint="/runtime/realtime-cognition" rootKey="realtime_cognition" description="Persistent cognition heartbeat and continuous reasoning streams." />;
}
