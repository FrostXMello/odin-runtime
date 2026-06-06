"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Deep Focus" subtitle="Focus sessions" endpoint="/runtime/operator-intelligence-v3" rootKey="operator_intelligence_v3" description="Deep work orchestration with interruption minimization." />;
}
