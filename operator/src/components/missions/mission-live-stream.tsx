"use client";

import { useMemo, useState, useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { runtimeApi } from "@/lib/api/runtime";
import { useOperatorStore } from "@/store/operator-store";
import { useMissionStream } from "@/hooks/useMissionStream";
import { useStreamStore } from "@/store/stream-store";
import { LiveIndicator } from "@/components/stream/live-indicator";
import { GlassPanel } from "@/components/ui/design-system";
import {
  signalError,
  signalVariantsForTier,
  microPress,
  transitionFast,
} from "@/components/ui/design-system/motion";
import { odinTypography } from "@/components/ui/design-system";
import type { MotionTier } from "@/hooks/useVisualPerformance";
import type { MissionSummary, TimelineEntry } from "@/lib/api/types";
import {
  missionUiPhase,
  phaseLabel,
  type MissionUiPhase,
} from "@/components/missions/mission-state";
import { isLifecycleNoise, isIssueSignal } from "@/lib/stream/event-filter";
import { cn } from "@/lib/utils/cn";

type Props = {
  missionId: string;
  summary?: MissionSummary;
  readOnly?: boolean;
  recovered?: boolean;
  onRecovered?: () => void;
  onStreamEvent?: () => void;
  motionTier?: MotionTier;
};

function SignalBlock({
  entry,
  isLatest,
  phase,
  motionTier,
}: {
  entry: TimelineEntry;
  isLatest: boolean;
  phase: MissionUiPhase;
  motionTier: MotionTier;
}) {
  const msg = entry.message?.trim();
  const isFailed = phase === "failed" && isLatest;
  const isExecuting = (phase === "running" || phase === "created") && isLatest;
  const injectVariants = signalVariantsForTier(motionTier);

  return (
    <motion.div
      variants={isFailed ? signalError : injectVariants}
      initial="hidden"
      animate={isFailed ? ["visible", "bloom"] : "visible"}
      className={cn(
        "group relative flex gap-3 py-2 pl-1",
        isLatest && "rounded-lg bg-odin-cyan/[0.03] px-2"
      )}
    >
      <div className="relative w-0.5 shrink-0 self-stretch overflow-hidden rounded-full bg-white/[0.04]">
        {isLatest && isExecuting && (
          <motion.div
            className="absolute inset-0 bg-odin-cyan/50"
            animate={{ opacity: [0.35, 0.75, 0.35] }}
            transition={{ duration: 2, repeat: Infinity, ease: [0.22, 1, 0.36, 1] }}
          />
        )}
        {isLatest && isFailed && (
          <motion.div
            className="absolute inset-0 bg-odin-rose/40"
            animate={{ opacity: [0.2, 0.45, 0.25] }}
            transition={{ duration: 2.8, repeat: Infinity, ease: [0.22, 1, 0.36, 1] }}
          />
        )}
        {isLatest && !isExecuting && !isFailed && (
          <motion.div
            className="absolute inset-0 bg-odin-cyan/30"
            initial={{ opacity: 0.7 }}
            animate={{ opacity: 0 }}
            transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          />
        )}
      </div>

      <div className="min-w-0 flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <span className={odinTypography.streamTime}>{entry.timestamp.slice(11, 19)}</span>
          <span
            className={cn(
              odinTypography.signalKind,
              "rounded-full px-2 py-0.5",
              isLatest ? "bg-odin-cyan/12 text-odin-cyan/90" : "bg-white/[0.03] text-slate-600"
            )}
          >
            {entry.kind}
          </span>
        </div>
        <p className={cn(odinTypography.streamLog, isLatest && "text-slate-300")}>
          {msg || entry.kind}
        </p>
      </div>
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
  motionTier = "full",
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
  const signalEntries = useMemo(
    () => entries.filter((e) => !isLifecycleNoise(e.kind)),
    [entries]
  );
  const issueEntries = useMemo(
    () => entries.filter((e) => isIssueSignal(e.kind)),
    [entries]
  );
  const prevLen = useRef(signalEntries.length);
  const entriesMounted = useRef(false);

  useEffect(() => {
    if (!entriesMounted.current) {
      entriesMounted.current = true;
      prevLen.current = entries.length;
      return;
    }
    if (signalEntries.length > prevLen.current) {
      onStreamEvent?.();
    }
    prevLen.current = signalEntries.length;
  }, [signalEntries.length, onStreamEvent]);

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
    <GlassPanel depth="stream" className={cn("mt-6 overflow-hidden", locked && "opacity-90")}>
      {recovered && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={transitionFast}
          className="border-b border-odin-emerald/15 bg-odin-emerald/08 px-5 py-2.5 text-xs text-odin-emerald/90"
        >
          Session restored — stream recalibrated
        </motion.div>
      )}

      <div className="border-b border-white/[0.04] px-5 py-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="truncate text-base font-semibold tracking-tight text-slate-100">{objective}</p>
            <p className="mt-1 font-mono text-[10px] text-slate-600">{missionId}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={cn("rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wide", statusBadge)}>
              {phaseLabel(phase)}
            </span>
            {!readOnly && <LiveIndicator channel={`mission:${missionId}`} />}
          </div>
        </div>
        {!readOnly && (
          <div className="mt-3 flex flex-wrap gap-2">
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
          <p className="mt-2 text-[10px] uppercase tracking-widest text-slate-600">Archive replay · locked</p>
        )}
      </div>

      <div className="max-h-[min(480px,50vh)] overflow-y-auto px-5 py-3">
        {isLoading && <p className="text-xs text-slate-500">Establishing signal channel…</p>}
        {!isLoading && signalEntries.length === 0 && (
          <p className="font-mono text-xs text-slate-600">Awaiting execution signals…</p>
        )}
        <div className="space-y-0.5">
          {signalEntries.map((entry, i) => (
            <SignalBlock
              key={`${entry.sort_key}-${entry.timestamp}`}
              entry={entry}
              isLatest={i === signalEntries.length - 1 && !locked}
              phase={phase}
              motionTier={motionTier}
            />
          ))}
        </div>
        {issueEntries.length > 0 && (
          <div className="mt-4 border-t border-odin-rose/10 pt-3">
            <p className="mb-2 text-[10px] uppercase tracking-widest text-odin-rose/70">
              Issues · {issueEntries.length}
            </p>
            <div className="space-y-0.5">
              {issueEntries.map((entry, i) => (
                <SignalBlock
                  key={`issue-${entry.sort_key}-${entry.timestamp}`}
                  entry={entry}
                  isLatest={i === issueEntries.length - 1}
                  phase="failed"
                  motionTier={motionTier}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-white/[0.04] px-5 py-2.5">
        <motion.button
          type="button"
          onClick={() => setTimelineOpen((v) => !v)}
          {...microPress}
          className="text-[10px] text-slate-600 hover:text-odin-cyan/80"
        >
          {timelineOpen ? "Collapse" : "Expand"} timeline · {signalEntries.length} signals
        </motion.button>
        <AnimatePresence>
          {timelineOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={transitionFast}
              className="overflow-hidden"
            >
              <div className="mt-2 max-h-28 space-y-0.5 overflow-y-auto pt-2">
                {entries.map((entry) => (
                  <p key={`scrub-${entry.sort_key}`} className="font-mono text-[9px] text-slate-700">
                    {entry.timestamp.slice(0, 19)} · {entry.kind}
                  </p>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </GlassPanel>
  );
}

function phaseBadgeClass(phase: MissionUiPhase): string {
  switch (phase) {
    case "running":
    case "created":
      return "bg-odin-cyan/10 text-odin-cyan ring-1 ring-odin-cyan/15";
    case "paused":
      return "bg-odin-amber/10 text-odin-amber ring-1 ring-odin-amber/15";
    case "failed":
      return "bg-odin-rose/10 text-odin-rose ring-1 ring-odin-rose/15";
    case "completed":
      return "bg-white/[0.03] text-slate-500 ring-1 ring-white/[0.05]";
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
    <motion.button
      type="button"
      onClick={onClick}
      {...microPress}
      className={cn(
        "rounded-lg px-2.5 py-1 text-[10px]",
        muted
          ? "text-slate-500 ring-1 ring-white/[0.05] hover:text-odin-cyan/80 hover:ring-odin-cyan/15"
          : "bg-odin-cyan/10 text-odin-cyan ring-1 ring-odin-cyan/20 hover:bg-odin-cyan/14"
      )}
    >
      {label}
    </motion.button>
  );
}
