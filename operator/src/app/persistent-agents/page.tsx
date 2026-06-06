"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Persistent Agents" subtitle="SQLite agents" endpoint="/runtime/persistent-agents" rootKey="persistent_agents" description="Supervised persistent agents with memory summaries and objectives." />;
}
