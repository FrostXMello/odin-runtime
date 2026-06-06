"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Pressure" subtitle="Pressure heatmap" endpoint="/runtime/execution-pressure" rootKey="runtime_execution_visibility" description="Execution pressure heatmaps and operational awareness rendering." />;
}
