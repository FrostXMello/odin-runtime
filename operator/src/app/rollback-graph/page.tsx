"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Rollback Graph" subtitle="Reversible DAG" endpoint="/runtime/rollback-graph" rootKey="execution_graph" description="Rollback graph generation for reversible execution lineage." />;
}
