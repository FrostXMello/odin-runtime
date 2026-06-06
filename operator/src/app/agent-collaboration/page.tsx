"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Agent Collaboration" subtitle="Multi-agent workflows" endpoint="/runtime/agent-collaboration/consensus" rootKey="agent_collaboration" description="Structured multi-agent collaboration with operator-visible reasoning." />;
}
