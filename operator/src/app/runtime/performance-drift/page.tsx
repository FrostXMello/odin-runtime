"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function PerformanceDriftPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "performance-drift"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/performance-drift"),
    refetchInterval: 12000,
  });
  const benchmarks = (data?.benchmarks as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Performance Drift</h2>
      <Card>
        <CardHeader title="Snapshots" subtitle={String(benchmarks.history_len ?? 0)} />
        <CardBody>
          <p className="text-xs text-slate-400">Compare versions over time — degradation alerts via regressions channel.</p>
        </CardBody>
      </Card>
    </div>
  );
}
