"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Cognitive Desktop"
      subtitle="Desktop client session"
      endpoint="/runtime/desktop-client"
      rootKey="desktop_client"
      description="Native desktop shell — persistent session, immersive modes, local backend bridge."
    />
  );
}
