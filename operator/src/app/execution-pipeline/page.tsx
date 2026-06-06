"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Pipeline" subtitle="Pipeline stages" endpoint="/runtime/execution-pipeline" rootKey="task_orchestration" description="Visual execution pipeline with adaptive task sequencing." />;
}
