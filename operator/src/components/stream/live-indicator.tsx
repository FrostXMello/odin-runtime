"use client";

import { Badge } from "@/components/ui/badge";
import { useStreamStore } from "@/store/stream-store";
import { cn } from "@/lib/utils/cn";

function statusVariant(
  status: string | undefined
): "healthy" | "degraded" | "critical" | "cyan" | "default" {
  if (status === "connected") return "healthy";
  if (status === "reconnecting" || status === "stale") return "degraded";
  if (status === "offline") return "critical";
  return "default";
}

export function LiveIndicator({ channel = "runtime" }: { channel?: string }) {
  const metrics = useStreamStore((s) => s.channels[channel]);
  const status = metrics?.status ?? "idle";
  const live = status === "connected";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant={live ? "cyan" : statusVariant(status)} pulse={live}>
        {live ? "LIVE" : status.toUpperCase()}
      </Badge>
      {metrics && (
        <>
          <span
            className={cn(
              "font-mono text-[10px]",
              status === "connected" ? "text-emerald-400/80" : "text-odin-muted"
            )}
          >
            {metrics.reconnectCount > 0 && `↻ ${metrics.reconnectCount} · `}
            {metrics.latencyMs != null && `${Math.round(metrics.latencyMs)}ms · `}
            {metrics.eventsPerSecond}/s · {metrics.eventCount} evt
          </span>
        </>
      )}
    </div>
  );
}

export function ConnectionHealthBadge({ channel = "runtime" }: { channel?: string }) {
  const status = useStreamStore((s) => s.channels[channel]?.status ?? "idle");
  const labels: Record<string, string> = {
    connected: "stream ok",
    reconnecting: "reconnecting",
    stale: "stale feed",
    offline: "offline",
    connecting: "connecting",
    idle: "polling",
  };
  return (
    <Badge variant={statusVariant(status)} className="normal-case">
      {labels[status] ?? status}
    </Badge>
  );
}
