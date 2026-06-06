"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Burnout Awareness" subtitle="Fatigue detection" endpoint="/runtime/operator-intelligence-v3" rootKey="operator_intelligence_v3" description="Transparent burnout risk detection and recovery." />;
}
