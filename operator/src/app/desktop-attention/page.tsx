"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Desktop Attention" subtitle="Attention routing" endpoint="/runtime/desktop-attention" rootKey="desktop_attention" description="Desktop-level salience scoring and surface prioritization." />;
}
