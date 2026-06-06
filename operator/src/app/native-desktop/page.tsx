"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Native Desktop" subtitle="Desktop persistence layer" endpoint="/runtime/native-desktop/status" rootKey="native_desktop" description="Native desktop runtime with tray coordination, notifications, and low-power awareness." />;
}
