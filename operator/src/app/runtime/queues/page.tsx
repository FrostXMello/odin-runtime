"use client";

import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { MetricTile } from "@/components/ui/metric-tile";

export default function RuntimeQueuesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "queues"],
    queryFn: () => runtimeApi.queues(),
    refetchInterval: 3000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Persistent queues</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricTile label="Scheduler backlog" value={data?.dispatch_queue_depth ?? 0} />
        <MetricTile label="Durable depth" value={data?.durable_depth ?? 0} />
        <MetricTile label="Retry queue" value={data?.retry_queue_depth ?? 0} />
        <MetricTile label="Stale requeues" value={data?.stale_requeues ?? 0} />
      </div>
      <Card>
        <CardHeader title="Due missions" subtitle={`persist=${String(data?.persist_enabled)}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          {(data?.due_missions ?? []).map((id) => (
            <div key={id}>{id.slice(0, 12)}…</div>
          ))}
          {!data?.due_missions?.length && <p>No missions due right now.</p>}
        </CardBody>
      </Card>
    </div>
  );
}
