"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Session Persistence" subtitle="Cross-restart recovery" endpoint="/runtime/session-persistence-v2" rootKey="session_persistence_v2" description="Session snapshot compression, SQLite optimization, and continuity hardening." />;
}
