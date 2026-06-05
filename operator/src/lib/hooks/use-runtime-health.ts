"use client";

import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { useOperatorStore } from "@/store/operator-store";
import { useStreamStore } from "@/store/stream-store";

function useRefetchInterval(): number | false {
  const live = useOperatorStore((s) => s.liveRefresh);
  const ms = useOperatorStore((s) => s.pollIntervalMs);
  const streamOn = useStreamStore((s) => s.runtimeConnected);
  if (!live) return false;
  return streamOn ? ms * 4 : ms;
}

export function useRuntimeHealth() {
  const refetchInterval = useRefetchInterval();
  return useQuery({
    queryKey: ["runtime", "health"],
    queryFn: () => runtimeApi.health(),
    refetchInterval,
    staleTime: 1000,
  });
}

export function useRuntimeIntrospection() {
  const refetchInterval = useRefetchInterval();
  return useQuery({
    queryKey: ["runtime", "introspection"],
    queryFn: () => runtimeApi.introspection(),
    refetchInterval,
    staleTime: 1000,
  });
}

export function useQueues() {
  const refetchInterval = useRefetchInterval();
  return useQuery({
    queryKey: ["runtime", "queues"],
    queryFn: () => runtimeApi.queues(),
    refetchInterval,
  });
}

export function useWorkers() {
  const refetchInterval = useRefetchInterval();
  return useQuery({
    queryKey: ["runtime", "workers"],
    queryFn: () => runtimeApi.workers(),
    refetchInterval,
  });
}

export function useBottlenecks() {
  const refetchInterval = useRefetchInterval();
  return useQuery({
    queryKey: ["runtime", "bottlenecks"],
    queryFn: () => runtimeApi.bottlenecks(),
    refetchInterval,
  });
}

export function useMissions() {
  const refetchInterval = useRefetchInterval();
  return useQuery({
    queryKey: ["missions"],
    queryFn: () => runtimeApi.missions(),
    refetchInterval: refetchInterval === false ? false : (refetchInterval as number) * 2,
  });
}
