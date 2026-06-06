"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Engineering Evolution" subtitle="Repo analysis" endpoint="/runtime/engineering-evolution" rootKey="engineering_evolution" description="Architecture drift, technical debt prediction, and supervised upgrade proposals." />;
}
