"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Deferred Reasoning" subtitle="Suspended chains" endpoint="/runtime/deferred-reasoning" rootKey="deferred_reasoning" description="SQLite-backed deferred reasoning persistence and recovery." />;
}
