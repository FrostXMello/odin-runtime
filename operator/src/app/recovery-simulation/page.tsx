"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Recovery Simulation" subtitle="Path simulator" endpoint="/runtime/recovery-simulation" rootKey="predictive_recovery" description="Recovery path simulation with supervised approval gates." />;
}
