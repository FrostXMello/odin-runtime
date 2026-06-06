"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  deriveMissionPhase,
  deriveOdinCorePhase,
  type OdinCoreInput,
  type OdinCorePhase,
} from "@/components/odin-core/odin-core-state";

const RESPONDING_MS = 650;
const COMPLETED_FADE_MS = 2200;

export function useOdinCorePerception(input: OdinCoreInput) {
  const [responding, setResponding] = useState(false);
  const [completedHold, setCompletedHold] = useState(false);
  const prevTick = useRef(input.streamEventTick);
  const prevState = useRef(input.missionState);

  useEffect(() => {
    if (input.streamEventTick === prevTick.current) return;
    prevTick.current = input.streamEventTick;
    if (!input.hasActiveStream || input.replayMode) return;
    setResponding(true);
    const t = window.setTimeout(() => setResponding(false), RESPONDING_MS);
    return () => window.clearTimeout(t);
  }, [input.streamEventTick, input.hasActiveStream, input.replayMode]);

  useEffect(() => {
    const state = input.missionState?.toLowerCase() ?? null;
    const was = prevState.current?.toLowerCase() ?? null;
    prevState.current = input.missionState;

    if (state === "completed" && was !== "completed") {
      setCompletedHold(true);
      const t = window.setTimeout(() => setCompletedHold(false), COMPLETED_FADE_MS);
      return () => window.clearTimeout(t);
    }
    if (state !== "completed") setCompletedHold(false);
  }, [input.missionState]);

  const missionPhase = useMemo(
    () => input.missionPhase ?? deriveMissionPhase(input.missionState),
    [input.missionPhase, input.missionState]
  );

  const phase: OdinCorePhase = useMemo(() => {
    if (completedHold) return "completed";
    return deriveOdinCorePhase({ ...input, missionPhase }, responding);
  }, [input, missionPhase, responding, completedHold]);

  return { phase, missionPhase };
}
