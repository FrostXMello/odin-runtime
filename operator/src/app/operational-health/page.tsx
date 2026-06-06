"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operational Health" subtitle="Global operational health" endpoint="/runtime/operational-health" rootKey="unified_command_center" description="Global operational health tracking across orchestration, execution, and governance layers." />;
}
