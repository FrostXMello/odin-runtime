"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Shared Command" subtitle="Synchronized command layer" endpoint="/runtime/shared-command" rootKey="shared_mission_control" description="Collaborative command synchronization across shared missions." />;
}
