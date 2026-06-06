"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Cleanup" subtitle="Stale state cleanup" endpoint="/runtime/runtime-cleanup/status" rootKey="runtime_cleanup" description="Orphan stream cleanup, replay cache cleanup, and background scheduling." />;
}
