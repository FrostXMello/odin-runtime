"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeLeasesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "leases"],
    queryFn: () => apiFetch<{ worker_id: string; lease_metrics: Record<string, number> }>("/runtime/leases"),
    refetchInterval: 3000,
  });

  const lm = data?.lease_metrics ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Active leases</h2>
      <Card>
        <CardHeader title="Lease coordinator" subtitle={`worker ${data?.worker_id ?? "—"}`} />
        <CardBody className="grid gap-2 sm:grid-cols-3 font-mono text-xs">
          <div>Acquired: {lm.leases_acquired ?? 0}</div>
          <div>Released: {lm.leases_released ?? 0}</div>
          <div>Stale requeued: {lm.stale_requeued ?? 0}</div>
          <div>Conflicts: {lm.lease_conflicts ?? 0}</div>
          <div>Renewed: {lm.leases_renewed ?? 0}</div>
        </CardBody>
      </Card>
    </div>
  );
}
