"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import type { MissionTimeline } from "@/lib/api/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

export function MissionWorkbenchHeader({
  missionId,
  timeline,
}: {
  missionId: string;
  timeline: MissionTimeline;
}) {
  const qc = useQueryClient();
  const lastEntry = timeline.entries[timeline.entries.length - 1];
  const lastEvent = lastEntry
    ? `${lastEntry.kind}${lastEntry.message ? ` — ${lastEntry.message}` : ""}`
    : "No events yet";

  const resume = useMutation({
    mutationFn: () => runtimeApi.resumeMission(missionId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mission-timeline", missionId] });
      qc.invalidateQueries({ queryKey: ["missions"] });
    },
  });

  const pause = useMutation({
    mutationFn: () => runtimeApi.pauseMission(missionId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mission-timeline", missionId] });
      qc.invalidateQueries({ queryKey: ["missions"] });
    },
  });

  const recover = useMutation({
    mutationFn: () => runtimeApi.recoverSession(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mission-timeline", missionId] });
      qc.invalidateQueries({ queryKey: ["missions"] });
    },
  });

  const canResume = ["paused", "blocked", "waiting"].includes(timeline.current_state);
  const canPause = ["running", "active"].includes(timeline.current_state);

  return (
    <Card glow>
      <CardHeader
        title="Mission control"
        subtitle={`State: ${timeline.current_state}`}
        action={<Badge>{timeline.current_state}</Badge>}
      />
      <CardBody className="space-y-3">
        <div>
          <p className="text-[10px] uppercase tracking-wide text-odin-muted">Lifecycle</p>
          <p className="mt-0.5 text-sm text-slate-200">{timeline.current_state}</p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wide text-odin-muted">Last execution event</p>
          <p className="mt-0.5 text-sm text-slate-300">{lastEvent}</p>
          <p className="mt-1 text-[10px] text-odin-muted">{timeline.entry_count} total events</p>
        </div>
        <div className="flex flex-wrap gap-2 pt-1">
          {canResume && (
            <ActionButton
              label={resume.isPending ? "Resuming…" : "Resume mission"}
              onClick={() => resume.mutate()}
              disabled={resume.isPending}
            />
          )}
          {canPause && (
            <ActionButton
              label={pause.isPending ? "Pausing…" : "Pause mission"}
              onClick={() => pause.mutate()}
              disabled={pause.isPending}
              muted
            />
          )}
          <ActionButton
            label={recover.isPending ? "Recovering…" : "Recover session"}
            onClick={() => recover.mutate()}
            disabled={recover.isPending}
            muted
          />
        </div>
        {recover.isSuccess && (
          <p className="text-xs text-emerald-400/90">Session recovery completed.</p>
        )}
      </CardBody>
    </Card>
  );
}

function ActionButton({
  label,
  onClick,
  disabled,
  muted,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  muted?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "rounded-lg border px-3 py-1.5 text-xs transition disabled:opacity-50",
        muted
          ? "border-odin-border/50 text-slate-400 hover:border-odin-cyan/40 hover:text-slate-200"
          : "border-odin-accent/50 bg-odin-accent/20 text-odin-cyan hover:bg-odin-accent/30"
      )}
    >
      {label}
    </button>
  );
}
