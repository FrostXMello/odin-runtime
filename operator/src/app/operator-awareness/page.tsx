"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operator Awareness" subtitle="Situational brief" endpoint="/runtime/operator-awareness" rootKey="operator_situational_awareness" description="High-level cognitive awareness and operational status visibility." />;
}
