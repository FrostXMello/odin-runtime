"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeOperationsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "operations"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/operations"),
    refetchInterval: 8000,
  });
  const ops = (data?.operations as Record<string, unknown>) ?? {};
  const project = useMutation({
    mutationFn: () => apiFetch("/runtime/operations/project", { method: "POST", body: JSON.stringify({ goal: "sustainability", horizon_weeks: 4 }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "operations"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Operational planning</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => project.mutate()}>Project roadmap</button>
      <Card>
        <CardHeader title="Scheduled" subtitle={`Items: ${String(ops.scheduled_items ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Multi-week planning and milestone forecasting</CardBody>
      </Card>
    </div>
  );
}
