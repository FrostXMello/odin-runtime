"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeSocietyPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "society"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/society"),
    refetchInterval: 8000,
  });
  const snap = (data?.snapshot as Record<string, unknown>) ?? {};

  const spawn = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/society/agents/spawn", {
        method: "POST",
        body: JSON.stringify({ name: "Saga", role: "research_analyst" }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "society"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Agent society</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => spawn.mutate()}
      >
        Spawn agent
      </button>
      <Card>
        <CardHeader title="Society graph" subtitle={`Agents: ${String(data?.agent_count ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Objectives: {String(data?.objective_count ?? 0)}</div>
          <div>Edges: {String((snap.collaboration_graph as Record<string, unknown>)?.edge_count ?? 0)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
