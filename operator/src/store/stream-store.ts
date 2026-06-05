"use client";

import { create } from "zustand";
import type { StreamConnectionStatus, StreamEnvelope } from "@/lib/stream/types";

const MAX_TICKER = 40;

export interface StreamChannelMetrics {
  channel: string;
  status: StreamConnectionStatus;
  reconnectCount: number;
  lastEventAt: number | null;
  lastHeartbeatAt: number | null;
  latencyMs: number | null;
  eventsPerSecond: number;
  eventCount: number;
}

interface StreamState {
  channels: Record<string, StreamChannelMetrics>;
  ticker: StreamEnvelope[];
  runtimeConnected: boolean;
  registerChannel: (channel: string) => void;
  patchChannel: (channel: string, patch: Partial<StreamChannelMetrics>) => void;
  pushEvent: (env: StreamEnvelope) => void;
  setRuntimeConnected: (on: boolean) => void;
}

function defaultMetrics(channel: string): StreamChannelMetrics {
  return {
    channel,
    status: "idle",
    reconnectCount: 0,
    lastEventAt: null,
    lastHeartbeatAt: null,
    latencyMs: null,
    eventsPerSecond: 0,
    eventCount: 0,
  };
}

export const useStreamStore = create<StreamState>((set, get) => ({
  channels: {},
  ticker: [],
  runtimeConnected: false,
  registerChannel: (channel) =>
    set((s) => ({
      channels: {
        ...s.channels,
        [channel]: s.channels[channel] ?? defaultMetrics(channel),
      },
    })),
  patchChannel: (channel, patch) =>
    set((s) => ({
      channels: {
        ...s.channels,
        [channel]: { ...(s.channels[channel] ?? defaultMetrics(channel)), ...patch },
      },
    })),
  pushEvent: (env) => {
    const ch = env.channel || "runtime";
    const now = Date.now();
    const prev = get().channels[ch] ?? defaultMetrics(ch);
    const dt = prev.lastEventAt ? (now - prev.lastEventAt) / 1000 : 1;
    const eps = dt > 0 ? 1 / dt : 0;
    const isHb = env.event_type === "heartbeat" || env.event_type === "connected";
    set((s) => ({
      ticker: isHb
        ? s.ticker
        : [env, ...s.ticker].slice(0, MAX_TICKER),
      channels: {
        ...s.channels,
        [ch]: {
          ...(s.channels[ch] ?? defaultMetrics(ch)),
          lastEventAt: now,
          lastHeartbeatAt: isHb ? now : s.channels[ch]?.lastHeartbeatAt ?? null,
          eventCount: (s.channels[ch]?.eventCount ?? 0) + 1,
          eventsPerSecond: Math.round(eps * 10) / 10,
          latencyMs:
            env.latency_ms ??
            (env.timestamp
              ? Math.max(0, now - new Date(env.timestamp).getTime())
              : s.channels[ch]?.latencyMs ?? null),
        },
      },
    }));
  },
  setRuntimeConnected: (runtimeConnected) => set({ runtimeConnected }),
}));
