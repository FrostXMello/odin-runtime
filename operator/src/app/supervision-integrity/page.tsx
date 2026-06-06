"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Supervision Integrity" subtitle="Integrity scoring" endpoint="/runtime/supervision-integrity" rootKey="trust_surfaces" description="Supervision integrity checks and intervention trust modeling." />;
}
