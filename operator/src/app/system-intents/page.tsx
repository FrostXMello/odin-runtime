"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="System Intents" subtitle="Intent routing" endpoint="/runtime/system-intents" rootKey="system_intents" description="File open/share intents and supervised system dispatch." />;
}
