"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Team Coordination" subtitle="Team synchronization" endpoint="/runtime/team-coordination" rootKey="team_coordination" description="Team attention balancing and cross-operator noise suppression." />;
}
