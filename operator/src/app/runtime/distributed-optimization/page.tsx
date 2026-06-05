"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeDistributedOptimizationPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "distributed-optimization"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/distributed-optimization"),
    refetchInterval: 8000,
  });
  const opt = (data?.optimization as Record<string, unknown>) ?? {};
  const optimize = useMutation({
    mutationFn: () => apiFetch("/runtime/distributed-optimization/optimize", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "distributed-optimization"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Distributed optimization</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => optimize.mutate()}>Rebalance</button>
      <Card>
        <CardHeader title="Federation load" subtitle={`Enabled: ${String(opt.enabled ?? false)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Topology, workload, and replication optimization</CardBody>
      </Card>
    </div>
  );
}
