"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Window Awareness" subtitle="Local window tracking" endpoint="/runtime/window-awareness/active" rootKey="window_awareness" description="Transparent, exclusion-aware active window and workspace transition monitoring." />;
}
