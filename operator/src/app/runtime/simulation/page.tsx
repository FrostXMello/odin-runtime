"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeSimulationPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "simulation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/world/simulation"),
    refetchInterval: 8000,
  });
  const sims = (data?.simulations as unknown[]) ?? [];

  const project = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/world/project", {
        method: "POST",
        body: JSON.stringify({ scenario: "mission_success", branches: 3 }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "simulation"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Simulation</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => project.mutate()}
      >
        Project scenario
      </button>
      <Card>
        <CardHeader title="Simulations" subtitle={`Runs: ${sims.length}`} />
        <CardBody className="font-mono text-xs text-slate-400">Bounded, reversible, confidence-scored</CardBody>
      </Card>
    </div>
  );
}
