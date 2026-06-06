"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Runtime Stability" subtitle="Instability cascade suppression" endpoint="/runtime/runtime-stability" rootKey="stability_loops" description="Adaptive stabilization density and low-power recovery scheduling." />;
}
