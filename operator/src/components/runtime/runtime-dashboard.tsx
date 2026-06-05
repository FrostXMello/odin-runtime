"use client";

import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { useRuntimeHealth, useBottlenecks, useQueues, useWorkers } from "@/lib/hooks/use-runtime-health";
import { runtimeApi } from "@/lib/api/runtime";
import { useOperatorStore } from "@/store/operator-store";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { MetricTile } from "@/components/ui/metric-tile";
import type { HealthStatus } from "@/lib/api/types";

function healthVariant(h: HealthStatus): "healthy" | "degraded" | "critical" | "default" {
  if (h === "healthy") return "healthy";
  if (h === "degraded") return "degraded";
  if (h === "critical") return "critical";
  return "default";
}

export function RuntimeDashboard() {
  const live = useOperatorStore((s) => s.liveRefresh);
  const poll = useOperatorStore((s) => s.pollIntervalMs);
  const health = useRuntimeHealth();
  const queues = useQueues();
  const workers = useWorkers();
  const bottlenecks = useBottlenecks();
  const execData = useQuery({
    queryKey: ["runtime", "executions"],
    queryFn: () => runtimeApi.executions(30),
    refetchInterval: live ? poll : false,
  });

  const h = health.data;
  const orch = h?.orchestration;
  const missions = h?.missions;
  const dispatcher = (missions?.dispatcher ?? {}) as Record<string, number>;
  const rt = missions?.runtime_metrics ?? {};

  const chartData = [
    { name: "waves", v: rt.waves_executed ?? 0 },
    { name: "done", v: rt.tasks_completed ?? 0 },
    { name: "fail", v: rt.tasks_failed ?? 0 },
    { name: "retry", v: rt.retries ?? 0 },
  ];

  if (health.isLoading) {
    return <p className="text-sm text-odin-muted">Connecting to Odin runtime…</p>;
  }
  if (health.isError) {
    return (
      <Card className="border-rose-500/40">
        <CardBody>
          <p className="text-rose-400">Backend unreachable. Start Odin API on port 8000.</p>
          <p className="mt-2 font-mono text-xs text-odin-muted">{String(health.error)}</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <Badge variant={healthVariant(h!.system_health)} pulse={live}>
          {h!.system_health}
        </Badge>
        <Badge variant={healthVariant(orch?.status ?? "default")}>
          orchestration {orch?.status}
        </Badge>
        <span className="text-xs text-odin-muted">
          Loop {h!.runtime_loop_health} · refresh {live ? `${poll / 1000}s` : "paused"}
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
        <MetricTile
          label="Active missions"
          value={missions?.active_missions ?? 0}
          sub={`${missions?.dispatchable_missions ?? 0} dispatchable`}
        />
        <MetricTile
          label="Queue depth"
          value={missions?.queue_depth ?? queues.data?.dispatch_queue_depth ?? 0}
          alert={(missions?.queue_depth ?? 0) > 20}
        />
        <MetricTile
          label="Throughput"
          value={(orch?.execution_throughput ?? 0).toFixed(2)}
          sub="tasks / wave"
          alert={orch?.zero_throughput}
        />
        <MetricTile
          label="Dup suppressed"
          value={orch?.duplicate_suppression_count ?? 0}
          alert={orch?.duplicate_loop_detected}
        />
        <MetricTile
          label="Active executions"
          value={execData.data?.metrics?.active_count ?? 0}
          sub={`${execData.data?.active_mission_executions?.length ?? 0} mission-linked`}
        />
        <MetricTile label="Recursion events" value={h!.recursion_events_detected} />
        <MetricTile
          label="Dispatcher util"
          value={`${Math.round((orch?.worker_utilization ?? dispatcher.worker_utilization ?? 0) * 100)}%`}
          sub={`${dispatcher.ticks ?? 0} ticks`}
        />
        <MetricTile label="Stuck missions" value={orch?.stuck_mission_count ?? 0} alert={(orch?.stuck_mission_count ?? 0) > 0} />
        <MetricTile label="Escalation rate" value={(orch?.escalation_rate ?? 0).toFixed(2)} />
        <MetricTile label="Signals" value={h!.signal_count} sub={`${h!.active_signal_chains} chains`} />
        <MetricTile
          label="Worker"
          value={workers.data?.workers.dispatcher_running ? "active" : "idle"}
          sub={workers.data?.workers.worker_mode}
        />
        <MetricTile label="Tasks completed" value={rt.tasks_completed ?? 0} />
        <MetricTile label="Retries" value={rt.retries ?? 0} alert={(rt.retries ?? 0) > 5} />
        <MetricTile
          label="Async in-flight"
          value={(dispatcher.async_runtime as Record<string, number> | undefined)?.active_futures ?? 0}
          sub={`${(dispatcher.async_runtime as Record<string, number> | undefined)?.submitted_async ?? 0} submitted`}
        />
        <MetricTile
          label="Dep unlocks"
          value={(dispatcher.async_runtime as Record<string, number> | undefined)?.dependency_releases ?? dispatcher.dependency_release_rate ?? 0}
        />
        <MetricTile
          label="Runtime wakeups"
          value={(dispatcher.async_runtime as Record<string, number> | undefined)?.wakeups ?? 0}
          sub={`${dispatcher.async_dispatches ?? 0} async waves`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Execution distribution" subtitle="Live runtime metrics" />
          <CardBody className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 10 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    background: "#0d111c",
                    border: "1px solid #1a2236",
                    borderRadius: 8,
                    fontSize: 11,
                  }}
                />
                <Area type="monotone" dataKey="v" stroke="#3b82f6" fill="url(#g)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        <Card>
          <CardHeader
            title="Bottlenecks"
            subtitle={`${bottlenecks.data?.count ?? 0} detected`}
          />
          <CardBody className="max-h-48 space-y-2 overflow-auto">
            {(bottlenecks.data?.bottlenecks ?? []).slice(0, 8).map((b) => (
              <div
                key={b.mission_id}
                className="rounded border border-odin-border/60 bg-odin-bg/50 px-2 py-1.5 text-xs"
              >
                <span className="font-mono text-odin-cyan">{b.mission_id.slice(0, 8)}</span>
                <span className="ml-2 text-amber-400">{b.reason}</span>
                <span className="ml-2 text-odin-muted">{b.state}</span>
              </div>
            ))}
            {!bottlenecks.data?.count && (
              <p className="text-xs text-odin-muted">No bottlenecks</p>
            )}
          </CardBody>
        </Card>
      </div>

      {h!.orchestration.warnings?.length > 0 && (
        <Card glow>
          <CardHeader title="Degradation warnings" />
          <CardBody>
            <ul className="space-y-1 text-sm text-amber-200/90">
              {h!.orchestration.warnings.map((w) => (
                <li key={w}>• {w}</li>
              ))}
            </ul>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
