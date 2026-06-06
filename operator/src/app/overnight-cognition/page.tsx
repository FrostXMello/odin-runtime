"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Overnight Cognition" subtitle="Runs while idle" endpoint="/runtime/overnight" rootKey="overnight_cognition" description="Bounded overnight cognition orchestration with low-power scheduling." />;
}
