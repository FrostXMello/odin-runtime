"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Global Pressure" subtitle="Command pressure balancing" endpoint="/runtime/global-pressure" rootKey="unified_command_center" description="Runtime pressure unification with adaptive synchronization throttling." />;
}
