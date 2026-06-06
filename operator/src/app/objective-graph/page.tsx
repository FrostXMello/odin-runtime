"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Objective Graph" subtitle="Dependency graph" endpoint="/runtime/objective-graph" rootKey="objective_management" description="Visual objective tree with dependency and checkpoint tracking." />;
}
