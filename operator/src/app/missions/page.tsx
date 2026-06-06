"use client";

import { Suspense, useCallback, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { useMissions } from "@/lib/hooks/use-runtime-health";
import { useOperatorStore } from "@/store/operator-store";
import { MissionCommandBar } from "@/components/missions/mission-command-bar";
import { MissionLiveStream } from "@/components/missions/mission-live-stream";
import { MissionCompletedList } from "@/components/missions/mission-completed-list";
import { splitMissions, missionUiPhase } from "@/components/missions/mission-state";
import { OdinCoreOrb } from "@/components/odin-core/odin-core-orb";
import { phaseLabel } from "@/components/odin-core/odin-core-state";
import { useOdinCorePerception, useActivityIntensity } from "@/hooks/useOdinCorePerception";
import { useEffectiveVisualMode } from "@/hooks/useVisualPerformance";
import { SurfaceLayer, type LayerDominance } from "@/components/ui/design-system";
import { layerReveal, microHover } from "@/components/ui/design-system/motion";
import { odinTypography } from "@/components/ui/design-system";
import { cn } from "@/lib/utils/cn";

function MissionsCommandSurface() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const missionParam = searchParams.get("mission");
  const replayMode = searchParams.get("replay") === "1";
  const focusMode = useOperatorStore((s) => s.focusMode);

  const [recovered, setRecovered] = useState(false);
  const [cmdFocused, setCmdFocused] = useState(false);
  const [cmdTyping, setCmdTyping] = useState(false);
  const [creating, setCreating] = useState(false);
  const [streamEventTick, setStreamEventTick] = useState(0);
  const [typingRippleKey, setTypingRippleKey] = useState(0);
  const [absorbKey, setAbsorbKey] = useState(0);
  const [eventTimes, setEventTimes] = useState<number[]>([]);

  const { motionTier, autoFallback } = useEffectiveVisualMode();
  const { data: missions, isLoading, isError } = useMissions();
  const { active, completed } = splitMissions(missions ?? []);

  const setMission = useCallback(
    (id: string | null, replay = false) => {
      setRecovered(false);
      if (!id) {
        router.replace("/missions");
        return;
      }
      const q = replay ? `?mission=${id}&replay=1` : `?mission=${id}`;
      router.replace(`/missions${q}`);
    },
    [router]
  );

  const focused =
    missions?.find((m) => m.mission_id === missionParam) ??
    active.find((m) => m.mission_id === missionParam);

  const showStream = Boolean(missionParam && focused);

  const { phase } = useOdinCorePerception({
    commandFocused: cmdFocused,
    commandTyping: cmdTyping,
    creating,
    missionState: focused?.current_state ?? null,
    missionPhase: focused ? missionUiPhase(focused.current_state) : null,
    streamEventTick,
    hasActiveStream: showStream,
    replayMode,
  });

  const activityIntensity = useActivityIntensity(eventTimes);

  const bumpStream = useCallback(() => {
    setStreamEventTick((n) => n + 1);
    setEventTimes((t) => [...t.slice(-12), Date.now()]);
  }, []);

  const handleTypingRipple = useCallback(() => {
    setTypingRippleKey((n) => n + 1);
  }, []);

  const handleSubmitPulse = useCallback(() => {
    setAbsorbKey((n) => n + 1);
  }, []);

  const layerFocus = useMemo((): {
    identity: LayerDominance;
    command: LayerDominance;
    execution: LayerDominance;
    archive: LayerDominance;
  } => {
    if (showStream) {
      return {
        identity: "background",
        command: cmdFocused ? "active" : "background",
        execution: "dominant",
        archive: "archive",
      };
    }
    if (cmdFocused || cmdTyping || creating) {
      return {
        identity: "active",
        command: "dominant",
        execution: "background",
        archive: "archive",
      };
    }
    return {
      identity: "dominant",
      command: "active",
      execution: "background",
      archive: "archive",
    };
  }, [showStream, cmdFocused, cmdTyping, creating]);

  const immersive = focusMode;

  return (
    <div className="odin-control-surface mx-auto flex min-h-[calc(100vh-6rem)] max-w-2xl flex-col px-1">
      <SurfaceLayer z="identity" dominance={layerFocus.identity} className="flex shrink-0 flex-col items-center pb-5 pt-2">
        <OdinCoreOrb
          phase={phase}
          motionTier={motionTier}
          pulseKey={streamEventTick}
          typingRippleKey={typingRippleKey}
          absorbKey={absorbKey}
          activityIntensity={activityIntensity}
        />
        <motion.p
          key={phase}
          animate={{ opacity: 1 }}
          className={cn(`${odinTypography.systemState} mt-1 text-odin-cyan/50`)}
        >
          System · {phaseLabel(phase)}
        </motion.p>
        {autoFallback && !immersive && (
          <p className="mt-1.5 text-[10px] text-slate-700">Intensity reduced · system adaptive</p>
        )}
      </SurfaceLayer>

      <SurfaceLayer z="command" dominance={layerFocus.command} className="shrink-0">
        <motion.div variants={layerReveal} initial="hidden" animate="visible">
          <MissionCommandBar
            onMissionCreated={(id) => setMission(id, false)}
            disabled={isLoading}
            onFocusChange={setCmdFocused}
            onTypingChange={setCmdTyping}
            onCreatingChange={setCreating}
            onTypingRipple={handleTypingRipple}
            onSubmitPulse={handleSubmitPulse}
            focused={cmdFocused}
            typing={cmdTyping}
            orbPhase={phase}
          />
        </motion.div>
      </SurfaceLayer>

      {isError && (
        <p className="mt-4 text-center text-xs text-odin-rose/90">System offline — start Odin API</p>
      )}

      <SurfaceLayer z="execution" dominance={layerFocus.execution} className="flex-1">
        {showStream && missionParam && (
          <MissionLiveStream
            missionId={missionParam}
            summary={focused}
            readOnly={replayMode}
            recovered={recovered}
            onRecovered={() => setRecovered(true)}
            onStreamEvent={bumpStream}
            motionTier={motionTier}
          />
        )}

        {!showStream && !isLoading && active.length > 0 && (
          <div className="mt-6 space-y-1">
            <p className={odinTypography.systemState}>Active processes</p>
            {active.map((m) => (
              <motion.button
                key={m.mission_id}
                type="button"
                onClick={() => setMission(m.mission_id, false)}
                {...microHover}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left ring-1 ring-white/[0.04] hover:ring-odin-cyan/12"
              >
                <span className="truncate text-sm text-slate-400">{m.objective}</span>
                <span className="ml-2 shrink-0 font-mono text-[10px] text-odin-cyan/60">{m.current_state}</span>
              </motion.button>
            ))}
          </div>
        )}

        {!showStream && !isLoading && !active.length && !completed.length && (
          <p className="mt-12 text-center font-mono text-xs text-slate-700">
            System idle · speak to the field above
          </p>
        )}
      </SurfaceLayer>

      {!(immersive && showStream) && (
        <SurfaceLayer z="archive" dominance={layerFocus.archive}>
          <MissionCompletedList
            missions={completed}
            onReplay={(id) => setMission(id, true)}
            showMiniCore={motionTier === "minimal"}
            collapsed={showStream}
          />
        </SurfaceLayer>
      )}
    </div>
  );
}

export default function MissionsPage() {
  return (
    <Suspense fallback={<p className="text-sm text-slate-600">Initializing control surface…</p>}>
      <MissionsCommandSurface />
    </Suspense>
  );
}
