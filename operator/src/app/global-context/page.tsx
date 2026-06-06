"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Global Context" subtitle="Context rebuild" endpoint="/runtime/global-context" rootKey="unified_cognitive_core" description="Rebuild unified operator context across runtimes." />;
}
