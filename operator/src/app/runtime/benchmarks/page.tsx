"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function BenchmarksPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "benchmarks"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/benchmarks"),
    refetchInterval: 12000,
  });
  const b = (data?.benchmarks as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Runtime Benchmarks</h2>
      <Card>
        <CardHeader title="History" subtitle={String(b.history_len ?? 0)} />
        <CardBody>
          <p className="text-xs text-slate-400">Cognition · Reasoning · Latency · Memory · Engineering · Autonomy</p>
        </CardBody>
      </Card>
    </div>
  );
}
