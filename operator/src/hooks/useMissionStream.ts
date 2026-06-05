"use client";

import { useRealtimeChannel } from "./useRealtimeChannel";

export function useMissionStream(missionId: string, enabled = true) {
  return useRealtimeChannel({
    path: `/missions/${missionId}`,
    channel: `mission:${missionId}`,
    enabled: enabled && Boolean(missionId),
  });
}

export function useTaskStream(taskId: string, enabled = true) {
  return useRealtimeChannel({
    path: `/tasks/${taskId}`,
    channel: `task:${taskId}`,
    enabled: enabled && Boolean(taskId),
  });
}

export function useTraceStream(traceId: string, enabled = true) {
  return useRealtimeChannel({
    path: `/traces/${traceId}`,
    channel: `trace:${traceId}`,
    enabled: enabled && Boolean(traceId),
  });
}
