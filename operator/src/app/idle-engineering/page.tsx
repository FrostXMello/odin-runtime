"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Idle Engineering" subtitle="Passive analysis" endpoint="/runtime/idle-engineering/report" rootKey="idle_engineering" description="Supervised repo analysis with no auto-deploy or patch apply." />;
}
