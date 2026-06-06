"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Autonomous Workflows" subtitle="Supervised loops" endpoint="/runtime/autonomous-workflows" rootKey="autonomous_workflows" description="Bounded autonomous workflow continuation with checkpointing." />;
}
