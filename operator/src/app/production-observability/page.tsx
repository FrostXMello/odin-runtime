"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Production Observability" subtitle="Runtime metrics" endpoint="/runtime/production-observability/metrics" rootKey="production_observability" description="Production telemetry, startup timing, and stream throughput metrics." />;
}
