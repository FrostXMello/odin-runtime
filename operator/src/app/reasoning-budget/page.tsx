"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Reasoning Budget" subtitle="Budget allocation" endpoint="/runtime/reasoning-budget" rootKey="cognitive_planning" description="Adaptive reasoning budget river with low-power planning modes." />;
}
