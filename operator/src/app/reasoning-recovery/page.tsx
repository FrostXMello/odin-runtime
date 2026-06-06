"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Reasoning Recovery" subtitle="Restore chains" endpoint="/runtime/reasoning-recovery" rootKey="deferred_reasoning" description="Restore interrupted reasoning chains and deferred objectives." />;
}
