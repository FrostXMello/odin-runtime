"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Repo Drift" subtitle="Architecture scan" endpoint="/runtime/idle-engineering/report" rootKey="idle_engineering" description="Passive architecture drift and refactor candidate detection." />;
}
