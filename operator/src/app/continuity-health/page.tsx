"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Continuity Health" subtitle="Health scoring" endpoint="/runtime/continuity-health" rootKey="mission_continuity" description="Long-horizon continuity health and interruption recovery metrics." />;
}
