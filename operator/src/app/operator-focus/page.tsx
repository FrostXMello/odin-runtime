"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operator Focus" subtitle="Deep work coordination" endpoint="/runtime/operator-focus/state" rootKey="operator_focus" description="Focus sessions, distraction pressure, and recovery recommendations." />;
}
