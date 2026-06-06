"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ActivityGraphPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "activity-graph"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/activity-graph"),
    refetchInterval: 8000,
  });
  const g = (data?.graph as Record<string, unknown>) ?? {};
  const graph = (g.graph as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Activity Graph</h2>
      <Card>
        <CardHeader title="Desktop flow" subtitle={`top: ${String(graph.top ?? "—")}`} />
        <CardBody className="text-xs text-slate-400">Privacy-preserving workstation activity graph</CardBody>
      </Card>
    </div>
  );
}
