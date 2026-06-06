"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Rollback Replay" subtitle="Execution replay analysis" endpoint="/runtime/rollback-replay" rootKey="rollback_intelligence" description="Bounded execution window replay with lazy hydration." />;
}
