"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Load Forecast" subtitle="Cognitive load" endpoint="/runtime/operator-intelligence-v4" rootKey="operator_intelligence_v4" description="Cognitive load forecasting for long work sessions." />;
}
