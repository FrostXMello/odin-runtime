"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Attention" subtitle="Routing engine" endpoint="/runtime/attention" rootKey="attention_engine" description="Salience scoring, focus weighting, and interruption classification." />;
}
