"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Conversations"
      subtitle="Persistent presence"
      endpoint="/runtime/conversational-presence"
      rootKey="conversational_presence"
      description="Continuous conversational operating layer with interruption handling and memory anchors."
    />
  );
}
