"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function SelfEvolutionPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "self-evolution"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/self-evolution"),
    refetchInterval: 8000,
  });
  const evo = (data?.evolution as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Self-Evolution Orchestrator</h2>
      <Card>
        <CardHeader title="Cycles" subtitle={String(evo.cycles ?? 0)} />
        <CardBody>
          <p className="text-xs text-amber-300/90">Supervised loops only — no direct main commits.</p>
          <p className="mt-2 text-xs text-slate-400">Stage: {String(evo.stage ?? "idle")}</p>
        </CardBody>
      </Card>
    </div>
  );
}
