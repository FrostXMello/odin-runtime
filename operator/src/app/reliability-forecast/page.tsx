"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Reliability Forecast" subtitle="Risk prediction" endpoint="/runtime/engineering-infrastructure" rootKey="engineering_infrastructure_v3" description="Reliability prediction and validation planning." />;
}
