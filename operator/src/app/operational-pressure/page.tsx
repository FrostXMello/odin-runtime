"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operational Pressure" subtitle="Pressure radar" endpoint="/runtime/operational-pressure" rootKey="operator_situational_awareness" description="Operational pressure forecasting and focus instability radar." />;
}
