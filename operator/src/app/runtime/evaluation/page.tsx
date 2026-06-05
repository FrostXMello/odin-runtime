"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function EvaluationPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "evaluation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/evaluation"),
    refetchInterval: 10000,
  });
  const ev = (data?.evaluation as Record<string, unknown>) ?? {};
  const run = useMutation({
    mutationFn: () => apiFetch("/runtime/evaluation/run", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "evaluation"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Self-evaluation</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => run.mutate()}>Run benchmarks</button>
      <Card>
        <CardHeader title="Benchmarks" subtitle={`Runs: ${String(ev.runs ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Regression detection and capability tracking</CardBody>
      </Card>
    </div>
  );
}
