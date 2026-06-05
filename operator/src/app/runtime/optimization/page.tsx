"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeOptimizationPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "optimization"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/optimization"),
    refetchInterval: 5000,
  });
  const run = useMutation({
    mutationFn: () => apiFetch<Record<string, unknown>>("/runtime/optimization/run", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "optimization"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Optimization cycles</h2>
      <button
        type="button"
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => run.mutate()}
      >
        Run cycle now
      </button>
      <Card>
        <CardBody className="font-mono text-xs text-slate-400">
          Completed cycles: {String(data?.cycles ?? 0)}
        </CardBody>
      </Card>
    </div>
  );
}
