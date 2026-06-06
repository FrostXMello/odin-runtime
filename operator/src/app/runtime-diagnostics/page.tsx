"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Diagnostics" subtitle="Health inspection" endpoint="/runtime/runtime-diagnostics/health" rootKey="runtime_diagnostics" description="Runtime health, sync validation, and checkpoint integrity." />;
}
