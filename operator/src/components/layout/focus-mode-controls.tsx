"use client";

import { useOperatorStore } from "@/store/operator-store";
import { cn } from "@/lib/utils/cn";

type Props = {
  className?: string;
};

/** Minimal floating controls when sidebar is hidden in focus mode. */
export function FocusModeControls({ className }: Props) {
  const { focusMode, visualMode, setFocusMode, setVisualMode } = useOperatorStore();

  return (
    <div
      className={cn(
        "fixed bottom-5 right-5 z-50 flex items-center gap-3 rounded-xl border border-white/[0.06] bg-odin-glass-strong px-3 py-2 backdrop-blur-lg shadow-odin-panel",
        className
      )}
    >
      <label className="flex cursor-pointer items-center gap-1.5 text-[10px] text-slate-500">
        <input
          type="checkbox"
          checked={visualMode}
          onChange={(e) => setVisualMode(e.target.checked)}
          className="accent-odin-cyan"
        />
        Visual
      </label>
      <span className="h-3 w-px bg-white/[0.08]" />
      <label className="flex cursor-pointer items-center gap-1.5 text-[10px] text-slate-500">
        <input
          type="checkbox"
          checked={focusMode}
          onChange={(e) => setFocusMode(e.target.checked)}
          className="accent-odin-cyan"
        />
        Focus
      </label>
    </div>
  );
}
