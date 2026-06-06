"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Consensus Center" subtitle="Agent consensus" endpoint="/runtime/consensus-center" rootKey="agent_collaboration" description="Execution consensus scoring and agent reasoning summaries." />;
}
