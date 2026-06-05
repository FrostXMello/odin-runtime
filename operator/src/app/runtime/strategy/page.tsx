"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeStrategyPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "strategy"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/strategy"),
    refetchInterval: 8000,
  });
  const strategy = (data?.strategy as Record<string, unknown>) ?? {};

  const analyze = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/strategy/analyze", {
        method: "POST",
        body: JSON.stringify({ goal: "optimize_runtime" }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "strategy"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Strategic reasoning</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => analyze.mutate()}
      >
        Analyze goal
      </button>
      <Card>
        <CardHeader title="Objectives" subtitle={`Count: ${String((strategy.objectives as unknown[])?.length ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Assumptions, uncertainty, causal justification</CardBody>
      </Card>
    </div>
  );
}
