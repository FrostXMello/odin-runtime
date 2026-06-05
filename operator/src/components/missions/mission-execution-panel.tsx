"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { executionsApi } from "@/lib/api/executions";
import { runtimeApi } from "@/lib/api/runtime";
import { apiFetch } from "@/lib/api/client";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

interface MissionExecutionsResponse {
  mission_id: string;
  count: number;
  executions: Array<{
    execution_id: string;
    task_id?: string;
    state: string;
    capability_used: string;
  }>;
  dependencies: {
    ready: string[];
    nodes: Array<{
      task_id: string;
      status: string;
      depends_on: string[];
      execution_id?: string;
    }>;
  };
}

export function MissionExecutionPanel({ missionId }: { missionId: string }) {
  const { data } = useQuery({
    queryKey: ["mission-executions", missionId],
    queryFn: () => apiFetch<MissionExecutionsResponse>(`/missions/${missionId}/executions`),
    refetchInterval: 3000,
  });

  if (!data) return null;

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader title="Task executions" subtitle={`${data.count} runs`} />
        <CardBody className="space-y-2">
          {data.executions.length === 0 && (
            <p className="text-xs text-odin-muted">No executions yet — tasks will run on next wave.</p>
          )}
          {data.executions.map((ex) => (
            <div
              key={ex.execution_id}
              className="flex items-center justify-between rounded border border-odin-border/50 px-2 py-1.5"
            >
              <Link
                href={`/executions/${ex.execution_id}`}
                className="font-mono text-[10px] text-odin-cyan hover:underline"
              >
                {ex.execution_id.slice(0, 10)}…
              </Link>
              <Badge>{ex.state}</Badge>
              <span className="text-[10px] text-odin-muted">{ex.capability_used}</span>
            </div>
          ))}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Dependency DAG" subtitle={`${data.dependencies.ready.length} ready`} />
        <CardBody>
          <DependencyGraph nodes={data.dependencies.nodes} ready={data.dependencies.ready} />
        </CardBody>
      </Card>
      <AsyncRuntimeMetrics missionId={missionId} />
    </div>
  );
}

function AsyncRuntimeMetrics({ missionId }: { missionId: string }) {
  const { data } = useQuery({
    queryKey: ["runtime", "health", "async"],
    queryFn: () => runtimeApi.health(),
    refetchInterval: 3000,
  });
  const asyncRt = (data?.missions?.dispatcher?.async_runtime ?? {}) as Record<string, number>;
  return (
    <Card className="lg:col-span-2">
      <CardHeader title="Async runtime" subtitle={`Mission ${missionId.slice(0, 8)}`} />
      <CardBody className="grid gap-2 sm:grid-cols-4">
        <Metric label="In-flight" value={asyncRt.active_futures ?? 0} />
        <Metric label="Submitted" value={asyncRt.submitted_async ?? 0} />
        <Metric label="Dep unlocks" value={asyncRt.dependency_releases ?? 0} />
        <Metric label="Wakeups" value={asyncRt.wakeups ?? 0} />
        <Metric label="Callbacks" value={asyncRt.callbacks_received ?? 0} />
        <Metric label="Dup suppressed" value={asyncRt.duplicate_callbacks_suppressed ?? 0} />
        <Metric label="Async waves" value={asyncRt.async_waves_dispatched ?? 0} />
        <Metric label="Concurrency" value={data?.missions?.dispatcher?.execution_concurrency ?? 0} />
      </CardBody>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border border-odin-border/40 px-2 py-1.5">
      <p className="text-[9px] uppercase text-odin-muted">{label}</p>
      <p className="font-mono text-sm text-slate-200">{value}</p>
    </div>
  );
}

function DependencyGraph({
  nodes,
  ready,
}: {
  nodes: MissionExecutionsResponse["dependencies"]["nodes"];
  ready: string[];
}) {
  const readySet = new Set(ready);
  return (
    <div className="space-y-1 font-mono text-[10px]">
      {nodes.map((n) => {
        const isRunning = ["running", "executing"].includes(n.status);
        const isReady = readySet.has(n.task_id);
        return (
        <div
          key={n.task_id}
          className={`rounded px-2 py-1 ${
            isRunning
              ? "bg-amber-500/10 text-amber-200"
              : isReady
                ? "bg-odin-cyan/10 text-odin-cyan"
                : "text-slate-400"
          }`}
        >
          <span>{n.task_id.slice(0, 8)}</span>
          <span className="mx-2 text-odin-muted">{n.status}</span>
          {n.depends_on.length > 0 && (
            <span className="text-odin-muted">← {n.depends_on.map((d) => d.slice(0, 6)).join(", ")}</span>
          )}
          {n.execution_id && (
            <Link href={`/executions/${n.execution_id}`} className="ml-2 text-odin-cyan">
              exec
            </Link>
          )}
        </div>
        );
      })}
    </div>
  );
}

export function MissionExecutionStdout({ executionId }: { executionId: string }) {
  const { data } = useQuery({
    queryKey: ["execution-logs", executionId],
    queryFn: () => executionsApi.logs(executionId, 80),
    refetchInterval: 2000,
  });
  if (!data?.stdout?.length) return null;
  return (
    <pre className="mt-2 max-h-24 overflow-auto rounded bg-odin-bg p-2 font-mono text-[10px] text-slate-400">
      {data.stdout.join("\n")}
    </pre>
  );
}
