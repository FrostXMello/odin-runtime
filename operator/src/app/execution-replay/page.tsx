"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Replay" subtitle="Replay chains" endpoint="/runtime/execution-replay" rootKey="execution_memory" description="Operational replay chains with lazy hydration." />;
}
