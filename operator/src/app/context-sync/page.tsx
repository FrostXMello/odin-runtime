"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Context Sync" subtitle="Surface synchronization" endpoint="/runtime/context-sync/state" rootKey="context_synchronization" description="Merges workspace context and cognitive surfaces across runtimes." />;
}
