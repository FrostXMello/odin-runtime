"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Workflow Forecast" subtitle="Completion probability" endpoint="/runtime/workflow-forecast" rootKey="execution_confidence" description="Workflow completion probability and mission success forecasting." />;
}
