"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Focus Recovery" subtitle="Breakdown recovery" endpoint="/runtime/focus-recovery" rootKey="operator_focus" description="Focus breakdown detection and operator-controlled recovery paths." />;
}
