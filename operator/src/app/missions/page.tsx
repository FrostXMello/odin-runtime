"use client";

import { Suspense, useCallback, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMissions } from "@/lib/hooks/use-runtime-health";
import { MissionCommandBar } from "@/components/missions/mission-command-bar";
import { MissionLiveStream } from "@/components/missions/mission-live-stream";
import { MissionCompletedList } from "@/components/missions/mission-completed-list";
import { splitMissions, missionUiPhase } from "@/components/missions/mission-state";
import { OdinCoreOrb } from "@/components/odin-core/odin-core-orb";
import { useOdinCorePerception } from "@/hooks/useOdinCorePerception";
import { useEffectiveVisualMode } from "@/hooks/useVisualPerformance";

function MissionsCommandSurface() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const missionParam = searchParams.get("mission");
  const replayMode = searchParams.get("replay") === "1";
  const [recovered, setRecovered] = useState(false);
  const [cmdFocused, setCmdFocused] = useState(false);
  const [cmdTyping, setCmdTyping] = useState(false);
  const [creating, setCreating] = useState(false);
  const [streamEventTick, setStreamEventTick] = useState(0);

  const { animationsEnabled, autoFallback } = useEffectiveVisualMode();
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

  const bumpStream = useCallback(() => {
    setStreamEventTick((n) => n + 1);
  }, []);

  return (
    <div className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-3xl flex-col">
      <header className="mb-2 shrink-0 text-center">
        <OdinCoreOrb
          phase={phase}
          animationsEnabled={animationsEnabled}
          pulseKey={streamEventTick}
          className="mb-3"
        />
        <h2 className="font-mono text-sm font-semibold tracking-wide text-odin-cyan">MISSION COMMAND</h2>
        <p className="mt-1 text-xs text-odin-muted">
          Command → execute → stream → complete. One surface, one context.
        </p>
        {autoFallback && (
          <p className="mt-1 text-[10px] text-slate-600">
            Visual performance mode — animations reduced automatically
          </p>
        )}
      </header>

      <MissionCommandBar
        onMissionCreated={(id) => setMission(id, false)}
        disabled={isLoading}
        onFocusChange={setCmdFocused}
        onTypingChange={setCmdTyping}
        onCreatingChange={setCreating}
      />

      {isError && (
        <p className="mt-3 text-xs text-rose-400">Backend unreachable — start Odin API to run missions.</p>
      )}

      {showStream && missionParam && (
        <MissionLiveStream
          missionId={missionParam}
          summary={focused}
          readOnly={replayMode}
          recovered={recovered}
          onRecovered={() => setRecovered(true)}
          onStreamEvent={bumpStream}
        />
      )}

      {!showStream && !isLoading && active.length > 0 && (
        <div className="mt-4 space-y-1">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            Active processes
          </p>
          {active.map((m) => (
            <button
              key={m.mission_id}
              type="button"
              onClick={() => setMission(m.mission_id, false)}
              className="flex w-full items-center justify-between rounded-lg border border-odin-border/40 bg-odin-panel/40 px-3 py-2 text-left transition hover:border-odin-cyan/40"
            >
              <span className="truncate text-xs text-slate-300">{m.objective}</span>
              <span className="ml-2 shrink-0 font-mono text-[10px] text-odin-cyan">{m.current_state}</span>
            </button>
          ))}
        </div>
      )}

      {!showStream && !isLoading && !active.length && !completed.length && (
        <p className="mt-6 text-center font-mono text-xs text-slate-500">
          No processes running. Enter a command above.
        </p>
      )}

      <MissionCompletedList
        missions={completed}
        onReplay={(id) => setMission(id, true)}
        showMiniCore={!animationsEnabled}
      />
    </div>
  );
}

export default function MissionsPage() {
  return (
    <Suspense fallback={<p className="text-sm text-odin-muted">Loading mission command…</p>}>
      <MissionsCommandSurface />
    </Suspense>
  );
}
