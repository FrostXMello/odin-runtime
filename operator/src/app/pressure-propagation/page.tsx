"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Pressure Propagation"
      subtitle="Runtime pressure diffusion"
      endpoint="/runtime/pressure-propagation/state"
      rootKey="pressure_propagation"
      description="Pressure diffusion visualization, congestion detection, and surface rebalancing."
    />
  );
}
