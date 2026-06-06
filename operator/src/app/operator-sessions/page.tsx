"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operator Sessions" subtitle="Collaborative session registry" endpoint="/runtime/operator-sessions/active" rootKey="operator_sessions" description="Operator identity, role, focus, approval authority, and session replay." />;
}
