"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronUp } from "lucide-react";
import { runtimeApi } from "@/lib/api/runtime";
import type { MissionSummary } from "@/lib/api/types";
import { outcomeLabel, missionUiPhase } from "@/components/missions/mission-state";
import { OdinCoreMini } from "@/components/odin-core/odin-core-orb";
import type { OdinCorePhase } from "@/components/odin-core/odin-core-state";
import { GlassPanel } from "@/components/ui/design-system";
import { microPress, transitionFast } from "@/components/ui/design-system/motion";
import { cn } from "@/lib/utils/cn";

type Props = {
  missions: MissionSummary[];
  onReplay: (missionId: string) => void;
  showMiniCore?: boolean;
  collapsed?: boolean;
};

function missionCorePhase(state: string): OdinCorePhase {
  const ui = missionUiPhase(state);
  if (ui === "completed") return "completed";
  if (ui === "failed") return "error";
  return "idle";
}

function CompletedRow({
  mission,
  onReplay,
  showMiniCore,
}: {
  mission: MissionSummary;
  onReplay: (id: string) => void;
  showMiniCore?: boolean;
}) {
  const { data: timeline } = useQuery({
    queryKey: ["mission-timeline", mission.mission_id, "snippet"],
    queryFn: () => runtimeApi.missionTimeline(mission.mission_id),
    staleTime: 60_000,
  });

  const last = timeline?.entries?.[timeline.entries.length - 1];
  const lastEvent = last
    ? `${last.kind}${last.message ? `: ${last.message}` : ""}`
    : mission.current_state;
  const outcome = outcomeLabel(mission.current_state);

  return (
    <div className="flex items-center justify-between gap-3 rounded-xl px-3 py-2 transition hover:bg-white/[0.02]">
      {showMiniCore && <OdinCoreMini phase={missionCorePhase(mission.current_state)} />}
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs text-slate-500">{mission.objective}</p>
        <p className="mt-0.5 truncate font-mono text-[10px] text-slate-700">{lastEvent}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <span
          className={cn(
            "text-[10px] uppercase tracking-wide",
            outcome === "success" ? "text-odin-emerald/70" : "text-odin-rose/70"
          )}
        >
          {outcome}
        </span>
        <motion.button
          type="button"
          onClick={() => onReplay(mission.mission_id)}
          {...microPress}
          className="rounded-lg px-2 py-0.5 text-[10px] text-odin-cyan/80 ring-1 ring-white/[0.06] hover:ring-odin-cyan/25 hover:text-odin-cyan"
        >
          Replay
        </motion.button>
      </div>
    </div>
  );
}

export function MissionCompletedList({ missions, onReplay, showMiniCore, collapsed: defaultCollapsed }: Props) {
  const [open, setOpen] = useState(!defaultCollapsed);

  if (!missions.length) return null;

  return (
    <div className="mt-auto pt-8">
      <GlassPanel depth="ambient" className="overflow-hidden">
        <motion.button
          type="button"
          onClick={() => setOpen((v) => !v)}
          {...microPress}
          className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-white/[0.02]"
        >
          <span className="text-[10px] font-medium uppercase tracking-[0.15em] text-slate-600">
            Archive · {missions.length} completed
          </span>
          <motion.span
            animate={{ rotate: open ? 0 : 180 }}
            transition={transitionFast}
          >
            <ChevronUp className="h-3.5 w-3.5 text-slate-600" />
          </motion.span>
        </motion.button>
        <AnimatePresence initial={false}>
          {open && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={transitionFast}
              className="overflow-hidden border-t border-white/[0.04]"
            >
              <div className="max-h-48 space-y-0.5 overflow-y-auto px-2 py-2">
                {missions.map((m) => (
                  <CompletedRow
                    key={m.mission_id}
                    mission={m}
                    onReplay={onReplay}
                    showMiniCore={showMiniCore}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassPanel>
    </div>
  );
}
