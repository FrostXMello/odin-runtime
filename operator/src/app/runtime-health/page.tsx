"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Health" subtitle="Health matrix" endpoint="/runtime/runtime-health" rootKey="runtime_diagnostics" description="Lightweight runtime health inspection and anomaly detection." />;
}
