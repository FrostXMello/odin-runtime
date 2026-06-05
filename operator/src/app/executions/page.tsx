"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { executionsApi } from "@/lib/api/executions";
import { useOperatorStore } from "@/store/operator-store";
import { useStreamStore } from "@/store/stream-store";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function ExecutionsPage() {
  const live = useOperatorStore((s) => s.liveRefresh);
  const poll = useOperatorStore((s) => s.pollIntervalMs);
  const runtimeConnected = useStreamStore((s) => s.runtimeConnected);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["executions"],
    queryFn: () => executionsApi.list(80),
    refetchInterval: live && !runtimeConnected ? poll : live ? poll * 3 : false,
  });

  const metrics = data?.metrics;
  const active =
    data?.executions.filter((e) =>
      ["running", "allocated", "queued", "retrying", "waiting"].includes(e.state)
    ).length ?? 0;

  const chartData = [
    { name: "done", v: metrics?.total_completed ?? 0 },
    { name: "fail", v: metrics?.total_failed ?? 0 },
    { name: "cancel", v: metrics?.total_cancelled ?? 0 },
    { name: "retry", v: metrics?.total_retries ?? 0 },
  ];

  if (isLoading) return <p className="text-odin-muted">Loading executions…</p>;
  if (isError) return <p className="text-rose-400">Failed to load executions</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <Badge variant="cyan" pulse={active > 0}>
          {active} active
        </Badge>
        <span className="text-xs text-odin-muted">
          throughput {metrics?.throughput_per_minute ?? 0}/min
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Stat label="Started" value={metrics?.total_started ?? 0} />
        <Stat label="Completed" value={metrics?.total_completed ?? 0} />
        <Stat label="Failed" value={metrics?.total_failed ?? 0} />
        <Stat label="Timed out" value={metrics?.total_timed_out ?? 0} />
        <Stat label="Active" value={metrics?.active_count ?? active} />
      </div>

      <Card>
        <CardHeader title="Execution throughput" subtitle="Cumulative counters" />
        <CardBody className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748b" }} />
              <YAxis tick={{ fontSize: 10, fill: "#64748b" }} />
              <Tooltip contentStyle={{ background: "#0d111c", border: "1px solid #1a2236" }} />
              <Area type="monotone" dataKey="v" stroke="#22d3ee" fill="#22d3ee33" />
            </AreaChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Recent executions" subtitle={`${data?.count ?? 0} records`} />
        <CardBody className="space-y-2 p-0">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-odin-border text-odin-muted">
              <tr>
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">State</th>
                <th className="px-4 py-2">Capability</th>
                <th className="px-4 py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {data?.executions.map((ex) => (
                <tr key={ex.execution_id} className="border-b border-odin-border/40 hover:bg-odin-border/20">
                  <td className="px-4 py-2 font-mono">
                    <Link href={`/executions/${ex.execution_id}`} className="text-odin-cyan hover:underline">
                      {ex.execution_id.slice(0, 8)}…
                    </Link>
                  </td>
                  <td className="px-4 py-2">
                    <Badge
                      variant={
                        ex.state === "completed"
                          ? "healthy"
                          : ex.state === "failed" || ex.state === "timed_out"
                            ? "critical"
                            : "default"
                      }
                    >
                      {ex.state}
                    </Badge>
                  </td>
                  <td className="px-4 py-2 text-slate-400">{ex.capability_used}</td>
                  <td className="px-4 py-2 text-odin-muted">
                    {new Date(ex.created_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-odin-border/60 bg-odin-panel/50 px-3 py-2">
      <p className="text-[10px] uppercase text-odin-muted">{label}</p>
      <p className="text-xl font-semibold text-slate-100">{value}</p>
    </div>
  );
}
