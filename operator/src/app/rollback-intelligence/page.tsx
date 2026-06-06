"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Rollback Intelligence" subtitle="Rollback graph generation" endpoint="/runtime/rollback-intelligence/graph" rootKey="rollback_intelligence" description="Rollback simulation, checkpoint selection, and confidence scoring." />;
}
