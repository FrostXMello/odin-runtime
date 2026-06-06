"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Supervision Confidence" subtitle="Confidence scoring" endpoint="/runtime/supervision-confidence" rootKey="operator_alignment" description="Supervision confidence and alignment drift detection dashboard." />;
}
