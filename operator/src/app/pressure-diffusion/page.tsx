"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Pressure Diffusion"
      subtitle="Overload propagation simulation"
      endpoint="/runtime/pressure-diffusion"
      rootKey="pressure_propagation"
      description="Simulate pressure diffusion and instability chain rendering across runtimes."
    />
  );
}
