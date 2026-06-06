"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Startup Profiler" subtitle="Startup timing" endpoint="/runtime/startup-profiler" rootKey="production_observability" description="Measure startup performance and optimization impact." />;
}
