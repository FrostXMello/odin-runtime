"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Operator Veto" subtitle="Recovery approval routing" endpoint="/runtime/operator-veto" rootKey="operator_veto" description="Operator intervention gates and trust-preserving escalation." />;
}
