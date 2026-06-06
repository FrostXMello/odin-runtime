"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Recovery Orchestration" subtitle="Supervised recovery coordination" endpoint="/runtime/recovery-orchestration" rootKey="recovery_orchestration" description="Bounded recovery execution with checkpoint restoration and phase transitions." />;
}
