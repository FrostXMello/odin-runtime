"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Metrics" subtitle="Operational metrics" endpoint="/runtime/runtime-metrics" rootKey="production_observability" description="Runtime load tracking and operational profiling." />;
}
