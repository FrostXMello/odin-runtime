"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface OperatorState {
  pollIntervalMs: number;
  liveRefresh: boolean;
  focusMode: boolean;
  visualMode: boolean;
  lowFpsDetected: boolean;
  setPollInterval: (ms: number) => void;
  setLiveRefresh: (on: boolean) => void;
  setFocusMode: (on: boolean) => void;
  setVisualMode: (on: boolean) => void;
  setLowFpsDetected: (on: boolean) => void;
}

const DEFAULT_POLL = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL_MS) || 3000;
const VISUAL_MODE_KEY = "odin_visual_mode";

function readVisualModeDefault(): boolean {
  if (typeof window === "undefined") return true;
  try {
    const raw = localStorage.getItem(VISUAL_MODE_KEY);
    if (raw !== null) return JSON.parse(raw) === true;
  } catch {
    /* ignore */
  }
  return true;
}

export const useOperatorStore = create<OperatorState>()(
  persist(
    (set) => ({
      pollIntervalMs: DEFAULT_POLL,
      liveRefresh: true,
      focusMode: false,
      visualMode: true,
      lowFpsDetected: false,
      setPollInterval: (pollIntervalMs) => set({ pollIntervalMs }),
      setLiveRefresh: (liveRefresh) => set({ liveRefresh }),
      setFocusMode: (focusMode) => set({ focusMode }),
      setVisualMode: (visualMode) => {
        if (typeof window !== "undefined") {
          localStorage.setItem(VISUAL_MODE_KEY, JSON.stringify(visualMode));
        }
        set({ visualMode });
      },
      setLowFpsDetected: (lowFpsDetected) => set({ lowFpsDetected }),
    }),
    {
      name: "odin-operator",
      partialize: (s) => ({
        pollIntervalMs: s.pollIntervalMs,
        liveRefresh: s.liveRefresh,
        focusMode: s.focusMode,
        visualMode: s.visualMode,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && typeof window !== "undefined") {
          state.visualMode = readVisualModeDefault();
        }
      },
    }
  )
);
