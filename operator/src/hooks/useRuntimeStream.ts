"use client";

import { useEffect } from "react";
import { useRealtimeChannel } from "./useRealtimeChannel";
import { useStreamStore } from "@/store/stream-store";

export function useRuntimeStream(enabled = true) {
  const setRuntimeConnected = useStreamStore((s) => s.setRuntimeConnected);
  const result = useRealtimeChannel({
    path: "/runtime",
    channel: "runtime",
    enabled,
  });

  useEffect(() => {
    const connected = result.metrics?.status === "connected";
    setRuntimeConnected(connected);
    return () => setRuntimeConnected(false);
  }, [result.metrics?.status, setRuntimeConnected]);

  return result;
}
