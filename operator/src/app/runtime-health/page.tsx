"use client";
import { useState } from "react";
import { RuntimeHealthSummary } from "@/components/health/runtime-health-summary";
import { DesktopExperiencePanel } from "@/components/desktop-experience/runtime-panel";

export default function Page() {
  const [showRaw, setShowRaw] = useState(false);

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <RuntimeHealthSummary />
      <button
        type="button"
        onClick={() => setShowRaw((v) => !v)}
        className="text-xs text-odin-muted hover:text-odin-cyan"
      >
        {showRaw ? "Hide raw diagnostics" : "Show raw diagnostics (debug)"}
      </button>
      {showRaw && (
        <DesktopExperiencePanel
          title="Runtime Health"
          subtitle="Health matrix"
          endpoint="/runtime/runtime-health"
          rootKey="runtime_diagnostics"
          description="P64 runtime health inspection payload."
        />
      )}
    </div>
  );
}
