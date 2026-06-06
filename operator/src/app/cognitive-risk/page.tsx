"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cognitive Risk" subtitle="Risk forecasting" endpoint="/runtime/cognitive-risk/forecast" rootKey="cognitive_risk" description="Cognitive overload forecasting and governance drift detection." />;
}
