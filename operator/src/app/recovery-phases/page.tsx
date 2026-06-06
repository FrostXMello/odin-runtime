"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Recovery Phases" subtitle="Recovery phase transitions" endpoint="/runtime/recovery-phases" rootKey="recovery_orchestration" description="Detection, stabilization, rollback review, recovery execution, validation, continuity restore." />;
}
