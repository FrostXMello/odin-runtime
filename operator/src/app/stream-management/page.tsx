"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Stream Management" subtitle="Channel compression" endpoint="/runtime/stream-management/compress" rootKey="stream_management" description="Stream multiplex compression, prioritization, and stale channel pruning." />;
}
