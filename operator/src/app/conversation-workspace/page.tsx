"use client";

import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  return (
    <DesktopExperiencePanel
      title="Conversation Workspace"
      subtitle="Unified chat + cognition"
      endpoint="/runtime/conversation-workspace"
      rootKey="conversation_workspace"
      description="Persistent chat, thought stream, reasoning graph, missions, and memory threads."
    />
  );
}
