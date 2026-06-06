"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Intervention Intelligence" subtitle="Intervention forecast" endpoint="/runtime/intervention-intelligence" rootKey="intervention_intelligence" description="Operator intervention forecasting and escalation risk estimation." />;
}
