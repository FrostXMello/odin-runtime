"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { executionsApi, type ExecutionRecord } from "@/lib/api/executions";
import { useExecutionStream } from "@/hooks/useExecutionStream";
import { useOperatorStore } from "@/store/operator-store";
import { LiveIndicator } from "@/components/stream/live-indicator";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { useStreamStore } from "@/store/stream-store";

function stateVariant(state: string): "healthy" | "degraded" | "critical" | "default" {
  if (state === "completed") return "healthy";
  if (state === "running" || state === "allocated") return "default";
  if (state === "failed" || state === "timed_out") return "critical";
  return "degraded";
}

export function ExecutionDetail({ executionId }: { executionId: string }) {
  const qc = useQueryClient();
  const live = useOperatorStore((s) => s.liveRefresh);
  const poll = useOperatorStore((s) => s.pollIntervalMs);
  const stream = useExecutionStream(executionId, live);
  const streamOn = stream.metrics?.status === "connected";
  const ticker = useStreamStore((s) => s.ticker);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["execution", executionId],
    queryFn: () => executionsApi.get(executionId),
    refetchInterval: live && !streamOn ? poll : false,
  });

  const { data: logs, refetch: refetchLogs } = useQuery({
    queryKey: ["execution-logs", executionId],
    queryFn: () => executionsApi.logs(executionId),
    refetchInterval: live && !streamOn ? poll : false,
  });

  const [stdoutLines, setStdoutLines] = useState<string[]>([]);
  const [stderrLines, setStderrLines] = useState<string[]>([]);

  useEffect(() => {
    if (logs?.stdout) setStdoutLines(logs.stdout);
    if (logs?.stderr) setStderrLines(logs.stderr);
  }, [logs]);

  useEffect(() => {
    const relevant = ticker.filter(
      (e) =>
        e.payload?.execution_id === executionId &&
        (e.event_type === "execution_stdout" || e.event_type === "execution_stderr")
    );
    if (!relevant.length) return;
    for (const ev of relevant.slice(0, 5)) {
      const line = String(ev.payload?.line ?? ev.message);
      if (ev.event_type === "execution_stderr") {
        setStderrLines((prev) => [...prev, line].slice(-500));
      } else {
        setStdoutLines((prev) => [...prev, line].slice(-500));
      }
    }
  }, [ticker, executionId]);

  const onCancel = useCallback(async () => {
    await executionsApi.cancel(executionId);
    await refetch();
  }, [executionId, refetch]);

  const onRetry = useCallback(async () => {
    await executionsApi.retry(executionId);
    qc.invalidateQueries({ queryKey: ["execution", executionId] });
  }, [executionId, qc]);

  const heartbeatAge = useMemo(() => {
    if (!data?.started_at) return null;
    return Math.round((Date.now() - new Date(data.started_at).getTime()) / 1000);
  }, [data?.started_at]);

  if (isLoading || !data) {
    return <p className="text-odin-muted">Loading execution…</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <Badge variant={stateVariant(data.state)} pulse={data.state === "running"}>
          {data.state}
        </Badge>
        <LiveIndicator channel={`execution:${executionId}`} />
        <span className="font-mono text-[10px] text-odin-muted">{data.capability_used}</span>
        {heartbeatAge != null && data.state === "running" && (
          <span className="text-[10px] text-emerald-400/80">♥ active {heartbeatAge}s</span>
        )}
        <div className="ml-auto flex gap-2">
          {["running", "allocated", "queued", "retrying"].includes(data.state) && (
            <button
              type="button"
              onClick={onCancel}
              className="rounded border border-rose-500/40 px-2 py-1 text-[10px] text-rose-400 hover:bg-rose-500/10"
            >
              Cancel
            </button>
          )}
          {["failed", "timed_out", "cancelled"].includes(data.state) && (
            <button
              type="button"
              onClick={onRetry}
              className="rounded border border-odin-cyan/40 px-2 py-1 text-[10px] text-odin-cyan hover:bg-odin-cyan/10"
            >
              Retry
            </button>
          )}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-4">
        <Metric label="Retries" value={`${data.retry_count}/${data.max_retries}`} />
        <Metric label="Exit" value={data.exit_code ?? "—"} />
        <Metric label="Agent" value={data.executor_agent} />
        <Metric label="Type" value={data.execution_type} />
      </div>

      {data.error && (
        <p className="rounded border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300">
          {data.error}
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <LogPanel title="stdout" lines={stdoutLines} onRefresh={() => refetchLogs()} />
        <LogPanel title="stderr" lines={stderrLines} variant="err" onRefresh={() => refetchLogs()} />
      </div>

      <Card>
        <CardHeader title="Result" />
        <CardBody>
          <pre className="max-h-40 overflow-auto font-mono text-[10px] text-slate-400">
            {JSON.stringify(data.result ?? {}, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-odin-border/60 bg-odin-panel/50 px-3 py-2">
      <p className="text-[10px] uppercase text-odin-muted">{label}</p>
      <p className="font-mono text-sm text-slate-200">{value}</p>
    </div>
  );
}

function LogPanel({
  title,
  lines,
  variant,
  onRefresh,
}: {
  title: string;
  lines: string[];
  variant?: "err";
  onRefresh: () => void;
}) {
  return (
    <Card className={variant === "err" ? "border-rose-500/20" : undefined}>
      <CardHeader
        title={title}
        subtitle={`${lines.length} lines`}
        action={
          <button type="button" onClick={onRefresh} className="text-[10px] text-odin-cyan">
            refresh
          </button>
        }
      />
      <CardBody>
        <pre
          className={`max-h-64 overflow-auto font-mono text-[10px] ${
            variant === "err" ? "text-rose-300/90" : "text-slate-300"
          }`}
        >
          {lines.length ? lines.join("\n") : "—"}
        </pre>
      </CardBody>
    </Card>
  );
}
