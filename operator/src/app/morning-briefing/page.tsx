"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Morning Briefing" subtitle="Startup summary" endpoint="/runtime/morning-briefing" rootKey="morning_briefing" description="Executive summary, overnight findings, and focus recommendations." />;
}
