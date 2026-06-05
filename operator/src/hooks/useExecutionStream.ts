"use client";

import { useRealtimeChannel } from "./useRealtimeChannel";

export function useExecutionStream(executionId: string, enabled = true) {
  return useRealtimeChannel({
    path: `/executions/${executionId}`,
    channel: `execution:${executionId}`,
    enabled: enabled && Boolean(executionId),
  });
}
