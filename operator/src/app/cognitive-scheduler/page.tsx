"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cog Scheduler" subtitle="Bounded queues" endpoint="/runtime/cognitive-scheduler" rootKey="cognitive_scheduler" description="Cognition budgeting, deferred queues, and overnight orchestration." />;
}
