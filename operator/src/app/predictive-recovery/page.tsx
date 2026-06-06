"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Predictive Recovery" subtitle="Failure forecasting" endpoint="/runtime/predictive-recovery/forecast" rootKey="predictive_recovery" description="Blocker forecasting and execution resilience scoring." />;
}
