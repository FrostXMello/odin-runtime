"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

const btn = "rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan";

export default function PerformancePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "performance"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/performance"),
    refetchInterval: 10000,
  });
  const optimize = useMutation({
    mutationFn: () => apiFetch<Record<string, unknown>>("/runtime/performance/optimize", { method: "POST" }),
  });
  const p = (data?.performance as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Performance</h2>
      <Card>
        <CardHeader title="Optimizations" subtitle={`${String(p.optimizations ?? 0)} cycles`} />
        <CardBody className="flex gap-2">
          <button type="button" className={btn} onClick={() => optimize.mutate()}>Optimize now</button>
        </CardBody>
      </Card>
    </div>
  );
}
