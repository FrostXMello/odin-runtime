"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return (
    <DesktopExperiencePanel title="Environment Intelligence" subtitle="Workspace understanding" endpoint="/runtime/environment-intelligence" rootKey="environment_intelligence" description="Operator intent inference, workflow prediction, and environment memory." />
  );
}
