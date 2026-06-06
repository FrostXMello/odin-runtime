"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Mission Command" subtitle="Mission-centric cognition" endpoint="/runtime/mission-command" rootKey="mission_command" description="Objective federation, mission DAG rendering, and strategic execution tracking." />;
}
