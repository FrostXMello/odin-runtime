"use client";

import { useMemo, useState, useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { runtimeApi } from "@/lib/api/runtime";
import { useOperatorStore } from "@/store/operator-store";
import { useMissionStream } from "@/hooks/useMissionStream";
import { useStreamStore } from "@/store/stream-store";
import { LiveIndicator } from "@/components/stream/live-indicator";
import type { MissionSummary, TimelineEntry } from "@/lib/api/types";
import {
  missionUiPhase,
  phaseLabel,
  streamBorderClass,
  type MissionUiPhase,
} from "@/components/missions/mission-state";

type Props = {
  missionId: string;
  summary?: MissionSummary;
  readOnly?: boolean;
  recovered?: boolean;
  onRecovered?: () => void;
  onStreamEvent?: () => void;
};

function formatEventLine(entry: TimelineEntry): string {
  const msg = entry.message?.trim();
  return msg ? `${entry.kind} — ${msg}` : entry.kind;
}

function StreamEvent({ entry, pulse }: { entry: TimelineEntry; pulse?: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`font-mono text-xs leading-relaxed ${
        pulse ? "rounded bg-odin-cyan/10 px-2 py-1 text-odin-cyan" : "text-slate-400"
      }`}
    >
      <span className="text-slate-600">{entry.timestamp.slice(11, 19)}</span>{" "}
      {formatEventLine(entry)}
    </motion.div>
  );
}

export function MissionLiveStream({
  missionId,
  summary,
  readOnly = false,
  recovered = false,
  onRecovered,
  onStreamEvent,
}: Props) {
  const qc = useQueryClient();
  const live = useOperatorStore((s) => s.liveRefresh);
  const interval = useOperatorStore((s) => s.pollIntervalMs);
  const [timelineOpen, setTimelineOpen] = useState(false);
  const stream = useMissionStream(missionId, live && !readOnly);
  const streamOn = stream.metrics?.status === "connected";

  const { data: timeline, isLoading } = useQuery({
    queryKey: ["mission-timeline", missionId],
    queryFn: () => runtimeApi.missionTimeline(missionId),
    refetchInterval: live && !readOnly && !streamOn ? interval : live && !readOnly ? interval * 2 : false,
  });

  const state = timeline?.current_state ?? summary?.current_state ?? "created";
  const phase = missionUiPhase(state);
  const locked = readOnly || phase === "completed" || phase === "failed";

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
      onRecovered?.();
    },
  });

  const entries = timeline?.entries ?? [];
  const latest = entries[entries.length - 1];
  const prior = entries.slice(0, -1);
  const prevLen = useRef(entries.length);
  const entriesMounted = useRef(false);

  useEffect(() => {
    if (!entriesMounted.current) {
      entriesMounted.current = true;
      prevLen.current = entries.length;
      return;
    }
    if (entries.length > prevLen.current) {
      onStreamEvent?.();
    }
    prevLen.current = entries.length;
  }, [entries.length, onStreamEvent]);

  const streamMetrics = useStreamStore((s) => s.channels[`mission:${missionId}`]);
  const prevEventAt = useRef<number | null>(null);
  const wsMounted = useRef(false);

  useEffect(() => {
    const at = streamMetrics?.lastEventAt ?? null;
    if (!wsMounted.current) {
      wsMounted.current = true;
      prevEventAt.current = at;
      return;
    }
    if (at !== null && at !== prevEventAt.current) {
      onStreamEvent?.();
    }
    prevEventAt.current = at;
  }, [streamMetrics?.lastEventAt, onStreamEvent]);

  const objective = summary?.objective ?? "Mission";

  const statusBadge = useMemo(() => phaseBadgeClass(phase), [phase]);

  return (
    <div
      className={`mt-4 overflow-hidden rounded-xl border border-odin-border/60 bg-odin-bg/50 border-l-4 ${streamBorderClass(phase)}`}
    >
      {recovered && (
        <div className="border-b border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-xs text-emerald-300">
          Session restored — continuing mission stream
        </div>
      )}

      <div className="border-b border-odin-border/40 px-4 py-3">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-100">{objective}</p>
            <p className="mt-0.5 font-mono text-[10px] text-odin-muted">{missionId}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`rounded px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${statusBadge}`}>
              {phaseLabel(phase)}
            </span>
            {!readOnly && <LiveIndicator channel={`mission:${missionId}`} />}
          </div>
        </div>
        {!readOnly && (
          <div className="mt-2 flex flex-wrap gap-2">
            {phase === "paused" && (
              <ActionBtn label={resume.isPending ? "Resuming…" : "Resume"} onClick={() => resume.mutate()} />
            )}
            {phase === "running" && (
              <ActionBtn label={pause.isPending ? "Pausing…" : "Pause"} muted onClick={() => pause.mutate()} />
            )}
            <ActionBtn
              label={recover.isPending ? "Recovering…" : "Recover session"}
              muted
              onClick={() => recover.mutate()}
            />
          </div>
        )}
        {readOnly && (
          <p className="mt-2 text-[10px] uppercase tracking-wide text-slate-500">Replay mode · stream locked</p>
        )}
      </div>

      <div className={`max-h-[420px] overflow-y-auto px-4 py-3 ${locked ? "opacity-75" : ""}`}>
        {isLoading && <p className="text-xs text-odin-muted">Connecting to mission stream…</p>}
        {!isLoading && entries.length === 0 && (
          <p className="font-mono text-xs text-slate-500">Awaiting execution events…</p>
        )}
        <div className="space-y-1">
          {prior.map((entry) => (
            <StreamEvent key={`${entry.sort_key}-${entry.timestamp}`} entry={entry} />
          ))}
          <AnimatePresence mode="popLayout">
            {latest && (
              <StreamEvent key={`${latest.sort_key}-pulse`} entry={latest} pulse={!locked} />
            )}
          </AnimatePresence>
        </div>
      </div>

      <div className="border-t border-odin-border/30 px-4 py-2">
        <button
          type="button"
          onClick={() => setTimelineOpen((v) => !v)}
          className="text-[10px] text-odin-muted hover:text-odin-cyan"
        >
          {timelineOpen ? "Hide" : "Show"} timeline scrub ({entries.length} events)
        </button>
        {timelineOpen && (
          <div className="mt-2 max-h-32 overflow-y-auto space-y-0.5 border-t border-odin-border/20 pt-2">
            {entries.map((entry) => (
              <p key={`scrub-${entry.sort_key}`} className="font-mono text-[9px] text-slate-600">
                {entry.timestamp.slice(0, 19)} · {entry.kind}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function phaseBadgeClass(phase: MissionUiPhase): string {
  switch (phase) {
    case "running":
    case "created":
      return "bg-odin-cyan/15 text-odin-cyan";
    case "paused":
      return "bg-amber-500/15 text-amber-300";
    case "failed":
      return "bg-rose-500/15 text-rose-400";
    case "completed":
      return "bg-slate-600/30 text-slate-400";
  }
}

function ActionBtn({
  label,
  onClick,
  muted,
}: {
  label: string;
  onClick: () => void;
  muted?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded border px-2 py-0.5 text-[10px] transition ${
        muted
          ? "border-odin-border/50 text-slate-400 hover:border-odin-cyan/40"
          : "border-odin-cyan/40 bg-odin-cyan/10 text-odin-cyan"
      }`}
    >
      {label}
    </button>
  );
}
