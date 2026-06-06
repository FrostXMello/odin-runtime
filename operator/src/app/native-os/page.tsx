"use client";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";
export default function Page() {
  return <DesktopExperiencePanel title="Native OS" subtitle="Desktop integration" endpoint="/runtime/native-os" rootKey="native_os" description="Tray, notifications, window state, and OS-level focus detection." />;
}
