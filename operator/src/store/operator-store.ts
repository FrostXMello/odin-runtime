"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface OperatorState {
  pollIntervalMs: number;
  liveRefresh: boolean;
  focusMode: boolean;
  setPollInterval: (ms: number) => void;
  setLiveRefresh: (on: boolean) => void;
  setFocusMode: (on: boolean) => void;
}

const DEFAULT_POLL = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL_MS) || 3000;

export const useOperatorStore = create<OperatorState>()(
  persist(
    (set) => ({
      pollIntervalMs: DEFAULT_POLL,
      liveRefresh: true,
      focusMode: false,
      setPollInterval: (pollIntervalMs) => set({ pollIntervalMs }),
      setLiveRefresh: (liveRefresh) => set({ liveRefresh }),
      setFocusMode: (focusMode) => set({ focusMode }),
    }),
    { name: "odin-operator" }
  )
);
