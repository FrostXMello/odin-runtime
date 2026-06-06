"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RegressionsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "regressions"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/regressions"),
    refetchInterval: 15000,
  });
  const history = (data?.history as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Regression Inspector</h2>
      <Card>
        <CardHeader title="Benchmark history" subtitle={`${history.length} snapshots`} />
        <CardBody>
          <p className="text-xs text-slate-400">Regression heatmap derived from benchmark drift.</p>
        </CardBody>
      </Card>
    </div>
  );
}
