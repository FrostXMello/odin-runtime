"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimePerceptionPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "perception"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/perception"),
    refetchInterval: 5000,
  });
  const context = (data?.context as Record<string, unknown>) ?? {};
  const metrics = (data?.metrics as Record<string, number>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Multimodal perception</h2>
      <Card>
        <CardHeader title="Unified context" subtitle={`Enabled: ${String(data?.enabled ?? false)}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Summary: {String(context.summary ?? "—")}</div>
          <div>Updates: {String(metrics.updates ?? 0)}</div>
          <div>Snapshots: {String(metrics.snapshots ?? 0)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
