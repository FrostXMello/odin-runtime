"use client";

import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import type { MissionSummary } from "@/lib/api/types";
import { outcomeLabel, missionUiPhase } from "@/components/missions/mission-state";
import { OdinCoreMini } from "@/components/odin-core/odin-core-orb";
import type { OdinCorePhase } from "@/components/odin-core/odin-core-state";

type Props = {
  missions: MissionSummary[];
  onReplay: (missionId: string) => void;
  showMiniCore?: boolean;
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
    <div className="flex items-center justify-between gap-3 rounded-lg border border-odin-border/30 bg-odin-panel/30 px-3 py-2 opacity-80">
      {showMiniCore && (
        <OdinCoreMini phase={missionCorePhase(mission.current_state)} />
      )}
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs text-slate-400">{mission.objective}</p>
        <p className="mt-0.5 truncate font-mono text-[10px] text-slate-600">{lastEvent}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <span
          className={`text-[10px] uppercase ${
            outcome === "success" ? "text-emerald-500/80" : "text-rose-400/80"
          }`}
        >
          {outcome}
        </span>
        <button
          type="button"
          onClick={() => onReplay(mission.mission_id)}
          className="rounded border border-odin-border/40 px-2 py-0.5 text-[10px] text-odin-cyan hover:border-odin-cyan/40"
        >
          Replay
        </button>
      </div>
    </div>
  );
}

export function MissionCompletedList({ missions, onReplay, showMiniCore }: Props) {
  if (!missions.length) return null;

  return (
    <div className="mt-8 border-t border-odin-border/40 pt-4">
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
        Completed · {missions.length}
      </p>
      <div className="space-y-1.5">
        {missions.map((m) => (
          <CompletedRow
            key={m.mission_id}
            mission={m}
            onReplay={onReplay}
            showMiniCore={showMiniCore}
          />
        ))}
      </div>
    </div>
  );
}
