"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operator Presence" subtitle="Live operator constellation" endpoint="/runtime/operator-presence" rootKey="operator_sessions" description="Operator presence, roles, approval authority, and focus state." />;
}
