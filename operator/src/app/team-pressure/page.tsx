"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Team Pressure" subtitle="Operator workload pressure" endpoint="/runtime/team-coordination/pressure" rootKey="team_coordination" description="Collaborative workload pressure and attention routing." />;
}
