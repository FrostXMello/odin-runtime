"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeReasoningPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "reasoning"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/reasoning"),
    refetchInterval: 8000,
  });
  const runtimeMetrics = (data?.runtime_metrics as Record<string, number>) ?? {};
  const embedMetrics = (data?.embedding_metrics as Record<string, number>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Memory-grounded reasoning</h2>
      <Card>
        <CardHeader title="Pipeline metrics" subtitle={String(data?.pipeline ?? "—")} />
        <CardBody className="font-mono text-xs text-slate-400">
          <div>Inferences: {runtimeMetrics.inferences ?? 0}</div>
          <div>Truncated: {runtimeMetrics.truncated ?? 0}</div>
          <div>Embeddings: {embedMetrics.embedded ?? 0}</div>
          <div>Searches: {embedMetrics.searches ?? 0}</div>
        </CardBody>
      </Card>
    </div>
  );
}
