"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Unified Core" subtitle="Orchestration" endpoint="/runtime/unified-core/status" rootKey="unified_cognitive_core" description="Central cognition orchestration loop and runtime synchronization." />;
}
