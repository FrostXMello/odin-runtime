"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Visibility" subtitle="Live telemetry" endpoint="/runtime/execution-visibility" rootKey="runtime_execution_visibility" description="Live execution visualization and stream compression." />;
}
