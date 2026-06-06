"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operator Alignment" subtitle="Assistance alignment" endpoint="/runtime/operator-alignment" rootKey="operator_alignment" description="Bounded adaptive assistance aligned with operator preferences." />;
}
