"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Graph" subtitle="DAG topology" endpoint="/runtime/execution-graph" rootKey="execution_graph" description="Execution DAG management with dependency tracking and pressure routing." />;
}
