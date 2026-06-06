"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Continuity Forecast" subtitle="Tomorrow's work" endpoint="/runtime/continuity-forecast" rootKey="continuity_forecasting" description="Predict bottlenecks, abandoned workflows, and operator focus." />;
}
