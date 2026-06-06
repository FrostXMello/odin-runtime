"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Overnight Summary" subtitle="Cycle report" endpoint="/runtime/overnight/summary" rootKey="overnight_cognition" description="Overnight cognition cycle summary and checkpoint state." />;
}
