"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Unified Command" subtitle="Command center coordination" endpoint="/runtime/unified-command/status" rootKey="unified_command_center" description="Unified runtime coordination with orchestration and governance fusion." />;
}
