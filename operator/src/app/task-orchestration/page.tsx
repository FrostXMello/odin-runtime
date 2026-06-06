"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Task Orchestration" subtitle="Execution queue" endpoint="/runtime/task-orchestration/queue" rootKey="task_orchestration" description="Multi-stage task pipelines with blocker detection and queue rebalancing." />;
}
