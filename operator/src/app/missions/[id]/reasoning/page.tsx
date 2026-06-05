"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function MissionReasoningPage() {
  const params = useParams();
  const missionId = params.id as string;

  const { data } = useQuery({
    queryKey: ["mission", missionId, "reasoning"],
    queryFn: () => apiFetch<Record<string, unknown>>(`/missions/${missionId}/reasoning`),
    refetchInterval: 3000,
  });

  const graph = (data?.reasoning_graph as Record<string, unknown>) ?? {};
  const nodes = (graph.nodes as Array<Record<string, unknown>>) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Reasoning graph · {missionId.slice(0, 12)}…</h2>
      <Card>
        <CardHeader title="Reasoning nodes" subtitle={`${nodes.length} nodes`} />
        <CardBody className="space-y-2 text-xs">
          {nodes.map((n) => (
            <div key={String(n.node_id)} className="rounded border border-odin-border/60 px-3 py-2 font-mono">
              <span className="text-odin-cyan">{String(n.kind)}</span> — {String(n.message)}
              <span className="ml-2 text-odin-muted">conf {String(n.confidence)}</span>
            </div>
          ))}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Planner context" />
        <CardBody className="font-mono text-xs text-slate-400">
          <pre className="whitespace-pre-wrap">{JSON.stringify(data?.planner_context, null, 2)}</pre>
        </CardBody>
      </Card>
    </div>
  );
}
