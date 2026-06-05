"use client";

import { useCallback, useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { wsChannelUrl } from "@/lib/stream/ws-url";
import { applyStreamEnvelope } from "@/lib/stream/cache-updates";
import type { StreamEnvelope, StreamConnectionStatus } from "@/lib/stream/types";
import { useStreamStore } from "@/store/stream-store";

const STALE_MS = 45_000;
const HEARTBEAT_STALE_MS = 35_000;
const MAX_BACKOFF_MS = 30_000;

export interface UseRealtimeChannelOptions {
  path: string;
  channel: string;
  enabled?: boolean;
  onEnvelope?: (env: StreamEnvelope) => void;
}

export function useRealtimeChannel({
  path,
  channel,
  enabled = true,
  onEnvelope,
}: UseRealtimeChannelOptions) {
  const qc = useQueryClient();
  const registerChannel = useStreamStore((s) => s.registerChannel);
  const patchChannel = useStreamStore((s) => s.patchChannel);
  const pushEvent = useStreamStore((s) => s.pushEvent);
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const staleTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const onEnvelopeRef = useRef(onEnvelope);
  onEnvelopeRef.current = onEnvelope;

  const setStatus = useCallback(
    (status: StreamConnectionStatus) => patchChannel(channel, { status }),
    [channel, patchChannel]
  );

  const connect = useCallback(() => {
    if (!enabled || typeof window === "undefined") return;
    registerChannel(channel);
    setStatus("connecting");
    const url = wsChannelUrl(path);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      backoffRef.current = 1000;
      setStatus("connected");
    };

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data as string) as StreamEnvelope;
        pushEvent(data);
        applyStreamEnvelope(qc, data);
        onEnvelopeRef.current?.(data);
        if (data.event_type === "heartbeat") {
          patchChannel(channel, { lastHeartbeatAt: Date.now() });
        }
      } catch {
        /* ignore malformed */
      }
    };

    ws.onerror = () => setStatus("offline");

    ws.onclose = () => {
      wsRef.current = null;
      const metrics = useStreamStore.getState().channels[channel];
      const nextReconnect = (metrics?.reconnectCount ?? 0) + 1;
      patchChannel(channel, {
        status: "reconnecting",
        reconnectCount: nextReconnect,
      });
      const delay = Math.min(backoffRef.current, MAX_BACKOFF_MS);
      backoffRef.current = Math.min(delay * 2, MAX_BACKOFF_MS);
      reconnectTimer.current = setTimeout(connect, delay);
    };
  }, [channel, enabled, path, patchChannel, pushEvent, qc, registerChannel, setStatus]);

  useEffect(() => {
    if (!enabled) {
      wsRef.current?.close();
      setStatus("idle");
      return;
    }
    connect();
    staleTimer.current = setInterval(() => {
      const m = useStreamStore.getState().channels[channel];
      if (!m || m.status !== "connected") return;
      const now = Date.now();
      const last = m.lastEventAt ?? 0;
      const lastHb = m.lastHeartbeatAt ?? last;
      if (now - last > STALE_MS) patchChannel(channel, { status: "stale" });
      else if (now - lastHb > HEARTBEAT_STALE_MS) patchChannel(channel, { status: "stale" });
    }, 5000);

    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 20_000);

    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (staleTimer.current) clearInterval(staleTimer.current);
      clearInterval(ping);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [channel, connect, enabled, patchChannel, setStatus]);

  const metrics = useStreamStore((s) => s.channels[channel]);

  return { metrics, channel };
}
