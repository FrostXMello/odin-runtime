"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Unfinished Work" subtitle="Abandoned items" endpoint="/runtime/unfinished-work" rootKey="continuity_forecasting" description="Detect abandoned workflows and unfinished priorities." />;
}
