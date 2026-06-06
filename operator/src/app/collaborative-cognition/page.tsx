"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Collaborative Cognition" subtitle="Multi-operator cognition" endpoint="/runtime/collaborative-cognition/state" rootKey="collaborative_cognition" description="Synchronized cognition surfaces and operator-aware shared attention." />;
}
