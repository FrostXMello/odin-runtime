"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Overlay Center" subtitle="Overlay management" endpoint="/runtime/overlay-center" rootKey="live_overlays_v2" description="Central overlay attach, suppress, and attention coordination." />;
}
