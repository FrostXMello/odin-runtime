"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Cognition Replay" subtitle="Cognition replay chains" endpoint="/runtime/cognition-replay" rootKey="live_cognition_timeline" description="Bounded cognition window replay with overnight timeline compression." />;
}
