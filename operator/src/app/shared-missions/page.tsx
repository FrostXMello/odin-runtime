"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Shared Missions" subtitle="Shared mission control" endpoint="/runtime/shared-mission-control" rootKey="shared_mission_control" description="Shared mission DAGs, ownership transfer, and command synchronization." />;
}
