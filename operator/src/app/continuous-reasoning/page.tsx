"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Continuous Reasoning" subtitle="Reasoning overlay" endpoint="/runtime/continuous-reasoning" rootKey="realtime_cognition" description="Continuous reasoning overlay with bounded cognition cycles." />;
}
