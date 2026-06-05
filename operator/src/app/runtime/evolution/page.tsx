"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeEvolutionPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "evolution"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/evolution"),
    refetchInterval: 8000,
  });
  const ev = (data?.evolution as Record<string, unknown>) ?? {};
  const optimize = useMutation({
    mutationFn: () => apiFetch("/runtime/evolution/optimize", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "evolution"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Runtime evolution</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => optimize.mutate()}>Optimize</button>
      <Card>
        <CardHeader title="Policy weights" subtitle={`Cycles: ${String(ev.cycles ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Behavioral adaptation only — no code modification</CardBody>
      </Card>
    </div>
  );
}
