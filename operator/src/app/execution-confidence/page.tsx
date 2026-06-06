"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Confidence" subtitle="Confidence estimation" endpoint="/runtime/execution-confidence" rootKey="execution_confidence" description="Execution certainty and rollback confidence scoring." />;
}
