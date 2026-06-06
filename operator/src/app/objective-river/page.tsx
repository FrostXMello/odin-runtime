"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Objective River" subtitle="Flow renderer" endpoint="/runtime/objective-river" rootKey="cognitive_visual_layers" description="Layered objective river with adaptive visual density." />;
}
