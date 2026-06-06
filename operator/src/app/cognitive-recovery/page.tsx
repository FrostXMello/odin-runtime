"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cognitive Recovery" subtitle="Recovery planning" endpoint="/runtime/operator-intelligence-v3" rootKey="operator_intelligence_v3" description="Cognitive fatigue prevention and recovery plans." />;
}
