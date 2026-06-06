"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  deriveMissionPhase,
  deriveOdinCorePhase,
  type OdinCoreInput,
  type OdinCorePhase,
} from "@/components/odin-core/odin-core-state";
import { ORB_AWARE_DELAY_S } from "@/components/ui/design-system/motion";

const RESPONDING_MS = 650;
const COMPLETED_FADE_MS = 2200;

const INSTANT_PHASES = new Set<OdinCorePhase>(["listening"]);

export function useOdinCorePerception(input: OdinCoreInput) {
  const [responding, setResponding] = useState(false);
  const [completedHold, setCompletedHold] = useState(false);
  const [displayPhase, setDisplayPhase] = useState<OdinCorePhase>("idle");
  const prevTick = useRef(input.streamEventTick);
  const prevState = useRef(input.missionState);
  const prevRawPhase = useRef<OdinCorePhase>("idle");

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

  const rawPhase: OdinCorePhase = useMemo(() => {
    if (completedHold) return "completed";
    return deriveOdinCorePhase({ ...input, missionPhase }, responding);
  }, [input, missionPhase, responding, completedHold]);

  useEffect(() => {
    const instant = INSTANT_PHASES.has(rawPhase);
    const delayMs = instant ? 0 : ORB_AWARE_DELAY_S * 1000;
    const t = window.setTimeout(() => {
      setDisplayPhase(rawPhase);
      prevRawPhase.current = rawPhase;
    }, delayMs);
    return () => window.clearTimeout(t);
  }, [rawPhase]);

  return { phase: displayPhase, rawPhase, missionPhase };
}

/** Stream event frequency → ambient orb intensity 0–1. */
export function useActivityIntensity(eventTimes: number[]): number {
  return useMemo(() => {
    const now = Date.now();
    const recent = eventTimes.filter((t) => now - t < 12_000);
    if (recent.length === 0) return 0;
    return Math.min(1, recent.length / 6);
  }, [eventTimes]);
}
