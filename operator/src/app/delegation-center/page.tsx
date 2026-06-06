"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Delegation Center" subtitle="Supervised delegation" endpoint="/runtime/delegation-engine" rootKey="delegation_engine" description="Approval-aware delegation with ownership tracking and rollback." />;
}
