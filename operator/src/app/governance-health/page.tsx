"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Governance Health" subtitle="Health scoring" endpoint="/runtime/governance-health" rootKey="predictive_governance" description="Governance health metrics and operational balancing." />;
}
