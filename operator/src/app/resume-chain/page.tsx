"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Resume Chain" subtitle="Workflow recovery" endpoint="/runtime/resume-chain" rootKey="workspace_sessions" description="Multi-step resume chain for interrupted workflows." />;
}
