"use client";

import { useEffect, useState } from "react";
import { useOperatorStore } from "@/store/operator-store";

const FPS_SAMPLE_FRAMES = 48;
const LOW_FPS_THRESHOLD = 30;

/** full = physics + glow; reduced = breath only; minimal = opacity/blend only (never dead). */
export type MotionTier = "full" | "reduced" | "minimal";

function detectLowPowerProfile(): boolean {
  if (typeof window === "undefined") return false;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return true;
  const cores = navigator.hardwareConcurrency ?? 8;
  return cores <= 4;
}

function sampleFps(): Promise<number> {
  return new Promise((resolve) => {
    const stamps: number[] = [];
    let count = 0;

    function frame(ts: number) {
      if (count > 0) stamps.push(ts);
      count += 1;
      if (count <= FPS_SAMPLE_FRAMES) {
        requestAnimationFrame(frame);
        return;
      }
      if (stamps.length < 2) {
        resolve(60);
        return;
      }
      const elapsed = stamps[stamps.length - 1] - stamps[0];
      const fps = ((stamps.length - 1) / elapsed) * 1000;
      resolve(fps);
    }

    requestAnimationFrame(frame);
  });
}

export function useEffectiveVisualMode() {
  const visualMode = useOperatorStore((s) => s.visualMode);
  const focusMode = useOperatorStore((s) => s.focusMode);
  const lowFpsDetected = useOperatorStore((s) => s.lowFpsDetected);
  const setLowFpsDetected = useOperatorStore((s) => s.setLowFpsDetected);
  const [lowPower, setLowPower] = useState(false);

  useEffect(() => {
    setLowPower(detectLowPowerProfile());
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    let cancelled = false;
    const idle = window.requestIdleCallback ?? ((cb: () => void) => window.setTimeout(cb, 800));
    const cancelIdle = window.cancelIdleCallback ?? window.clearTimeout;

    const handle = idle(async () => {
      const fps = await sampleFps();
      if (!cancelled && fps < LOW_FPS_THRESHOLD) setLowFpsDetected(true);
    });

    return () => {
      cancelled = true;
      cancelIdle(handle as number);
    };
  }, [setLowFpsDetected]);

  const autoFallback = lowFpsDetected || (focusMode && lowPower);

  const motionTier: MotionTier = lowFpsDetected || !visualMode
    ? "minimal"
    : focusMode
      ? "reduced"
      : "full";

  /** Legacy compat — never fully kills motion. */
  const animationsEnabled = motionTier !== "minimal" || visualMode;

  return {
    animationsEnabled: true,
    motionTier,
    autoFallback,
    lowFpsDetected,
    lowPower,
    focusMode,
    visualMode,
  };
}
