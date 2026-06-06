"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Stability Loops" subtitle="Bounded stabilization loops" endpoint="/runtime/stability-loops" rootKey="stability_loops" description="Runtime cooldown coordination and recovery throttling." />;
}
