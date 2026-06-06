"use client";

import { useRuntimeHealth } from "@/lib/hooks/use-runtime-health";
import { useStreamStore } from "@/store/stream-store";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import type { HealthStatus } from "@/lib/api/types";

type Overall = "ok" | "degraded" | "broken";

function deriveOverall(
  systemHealth?: HealthStatus,
  orchestrationStatus?: HealthStatus,
  rcaStatus?: HealthStatus
): Overall {
  const statuses = [systemHealth, orchestrationStatus, rcaStatus].filter(Boolean);
  if (statuses.some((s) => s === "critical")) return "broken";
  if (statuses.some((s) => s === "degraded")) return "degraded";
  return "ok";
}

const OVERALL_COPY: Record<
  Overall,
  { title: string; subtitle: string; variant: "healthy" | "degraded" | "critical" }
> = {
  ok: {
    title: "System OK",
    subtitle: "Runtime is healthy — keep working on missions",
    variant: "healthy",
  },
  degraded: {
    title: "System Degraded",
    subtitle: "Something is slow or stuck — check missions before diving deeper",
    variant: "degraded",
  },
  broken: {
    title: "System Broken",
    subtitle: "Critical issue detected — recover session or restart backend",
    variant: "critical",
  },
};

function plainMemory(data: ReturnType<typeof useRuntimeHealth>["data"]): string {
  const gc = data?.missions?.gc;
  if (gc && typeof gc === "object") {
    const archived = Number((gc as Record<string, number>).archived ?? 0);
    const orphans = Number((gc as Record<string, number>).orphans_removed ?? 0);
    if (archived > 0 || orphans > 0) {
      return `GC active (${archived} archived)`;
    }
  }
  const active = data?.missions?.active_missions ?? 0;
  return active > 0 ? `${active} active mission(s) in memory` : "Light memory load";
}

function plainWorker(data: ReturnType<typeof useRuntimeHealth>["data"]): string {
  const dispatcher = data?.missions?.dispatcher as Record<string, unknown> | undefined;
  const workerMode = String(dispatcher?.worker_mode ?? "unknown");
  const queueDepth = data?.missions?.queue_depth ?? 0;
  if (workerMode.includes("disabled") || workerMode === "off") {
    return queueDepth > 0
      ? `Worker off · ${queueDepth} queued (resume manually)`
      : "Worker off · missions run on create/resume";
  }
  if (queueDepth > 0) return `Worker active · ${queueDepth} queued`;
  return "Worker active · queue empty";
}

export function RuntimeHealthSummary() {
  const { data, isLoading, isError } = useRuntimeHealth();
  const streamConnected = useStreamStore((s) => s.runtimeConnected);

  if (isLoading) {
    return (
      <Card glow>
        <CardBody>
          <p className="text-sm text-odin-muted">Checking system health…</p>
        </CardBody>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card glow>
        <CardHeader title="System Broken" subtitle="Cannot reach Odin backend" />
        <CardBody>
          <p className="text-xs text-rose-400">Start the backend and refresh this page.</p>
        </CardBody>
      </Card>
    );
  }

  const overall = deriveOverall(
    data.system_health,
    data.orchestration?.status,
    data.root_cause_analysis?.status
  );
  const copy = OVERALL_COPY[overall];

  return (
    <Card glow>
      <CardHeader
        title={copy.title}
        subtitle={copy.subtitle}
        action={<Badge variant={copy.variant}>{overall.toUpperCase()}</Badge>}
      />
      <CardBody>
        <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <HealthFact label="Overall" value={data.system_health ?? "unknown"} />
          <HealthFact label="Memory" value={plainMemory(data)} />
          <HealthFact
            label="Live stream"
            value={streamConnected ? "Connected" : "Disconnected (polling fallback)"}
            warn={!streamConnected}
          />
          <HealthFact label="Mission worker" value={plainWorker(data)} />
        </dl>
        {data.root_cause_analysis?.summary && overall !== "ok" && (
          <p className="mt-3 rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-xs text-amber-200/90">
            {data.root_cause_analysis.summary}
          </p>
        )}
      </CardBody>
    </Card>
  );
}

function HealthFact({
  label,
  value,
  warn,
}: {
  label: string;
  value: string;
  warn?: boolean;
}) {
  return (
    <div className="rounded-lg border border-odin-border/40 bg-odin-bg/30 px-3 py-2">
      <dt className="text-[10px] uppercase tracking-wide text-odin-muted">{label}</dt>
      <dd className={`mt-0.5 text-sm capitalize ${warn ? "text-amber-300" : "text-slate-200"}`}>
        {value}
      </dd>
    </div>
  );
}
