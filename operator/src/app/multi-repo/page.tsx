"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Multi Repo" subtitle="Cross-repo reasoning" endpoint="/runtime/engineering-evolution-v2" rootKey="engineering_evolution_v2" description="Supervised multi-repository architecture reasoning." />;
}
