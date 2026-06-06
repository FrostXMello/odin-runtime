"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Mission Phases" subtitle="Operational phase transitions" endpoint="/runtime/mission-phases" rootKey="mission_command" description="Planning, execution, recovery, stabilization, overnight, and supervision review phases." />;
}
