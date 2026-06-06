"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Attention Flow" subtitle="Adaptive routing" endpoint="/runtime/realtime-cognition" rootKey="attention_flow" description="Real-time attention routing and context-aware prioritization." />;
}
