"use client";

import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import type { MissionSummary } from "@/lib/api/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";

const ACTIVE = new Set(["running", "active", "waiting", "blocked", "paused", "pending"]);

function stateVariant(state: string): "healthy" | "degraded" | "critical" | "default" {
  if (state.includes("fail") || state === "cancelled") return "critical";
  if (state === "blocked" || state === "paused") return "degraded";
  if (state === "completed") return "healthy";
  return "default";
}

export function MissionRow({ mission }: { mission: MissionSummary }) {
  const qc = useQueryClient();
  const isActive = ACTIVE.has(mission.current_state);

  const { data: timeline } = useQuery({
    queryKey: ["mission-timeline", mission.mission_id, "snippet"],
    queryFn: () => runtimeApi.missionTimeline(mission.mission_id),
    enabled: isActive,
    staleTime: 5000,
  });

  const resume = useMutation({
    mutationFn: () => runtimeApi.resumeMission(mission.mission_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["missions"] });
      qc.invalidateQueries({ queryKey: ["mission-timeline", mission.mission_id] });
    },
  });

  const lastEntry = timeline?.entries?.[timeline.entries.length - 1];
  const lastLabel = lastEntry
    ? `${lastEntry.kind}${lastEntry.message ? `: ${lastEntry.message}` : ""}`
    : null;

  return (
    <div className="rounded-lg border border-odin-border/60 bg-odin-bg/40 px-4 py-3 transition-colors hover:border-odin-cyan/30 hover:bg-odin-panel/50">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <Link href={`/missions/${mission.mission_id}`} className="min-w-0 flex-1">
          <p className="truncate text-sm text-slate-200">{mission.objective}</p>
          <p className="mt-1 font-mono text-[10px] text-odin-muted">{mission.mission_id}</p>
        </Link>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <Badge variant={stateVariant(mission.current_state)}>{mission.current_state}</Badge>
          <span className="text-[10px] text-odin-muted">
            {mission.active_tasks.length} active · {mission.completed_tasks.length} done
          </span>
        </div>
      </div>
      {lastLabel && (
        <p className="mt-2 truncate text-xs text-slate-400">
          <span className="text-odin-muted">Last event · </span>
          {lastLabel}
        </p>
      )}
      <div className="mt-2 flex flex-wrap gap-2">
        <Link
          href={`/missions/${mission.mission_id}`}
          className="rounded border border-odin-border/50 px-2 py-0.5 text-[10px] text-odin-cyan hover:border-odin-cyan/40"
        >
          Open
        </Link>
        {(mission.current_state === "paused" || mission.current_state === "blocked") && (
          <button
            type="button"
            onClick={() => resume.mutate()}
            disabled={resume.isPending}
            className={cn(
              "rounded border border-odin-border/50 px-2 py-0.5 text-[10px] text-slate-300 hover:border-odin-cyan/40",
              resume.isPending && "opacity-50"
            )}
          >
            {resume.isPending ? "Resuming…" : "Resume"}
          </button>
        )}
      </div>
    </div>
  );
}
