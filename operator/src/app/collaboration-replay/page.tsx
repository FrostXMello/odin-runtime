"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Collaboration Replay" subtitle="Collaborative session replay" endpoint="/runtime/collaboration-replay" rootKey="operator_sessions" description="Bounded collaborative replay with lazy hydration and compression." />;
}
