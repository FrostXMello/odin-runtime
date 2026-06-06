"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Command Surfaces" subtitle="Unified command HUD" endpoint="/runtime/command-surfaces" rootKey="operator_command_surfaces" description="Cinematic operational rendering with governance and execution overlays." />;
}
