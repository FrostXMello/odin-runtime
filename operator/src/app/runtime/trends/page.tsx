"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeTrendsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "trends"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/trends"),
    refetchInterval: 12000,
  });
  const trends = (data?.trends as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Trends</h2>
      <Card>
        <CardHeader title="Trend analysis" subtitle={`Topic: ${String(data?.topic || "—")}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Signals: {trends.length}
        </CardBody>
      </Card>
    </div>
  );
}
