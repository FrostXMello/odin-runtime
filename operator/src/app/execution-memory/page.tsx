"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Execution Memory" subtitle="Execution history" endpoint="/runtime/execution-memory/history" rootKey="execution_memory" description="Persistent execution chains with successful pattern resurfacing." />;
}
