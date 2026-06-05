"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeCognitionPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "cognition"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognition"),
    refetchInterval: 5000,
  });
  const graph = (data?.memory_graph as Record<string, unknown>) ?? {};
  const entities = (graph.entities as Array<Record<string, unknown>>) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Cognitive memory graph</h2>
      <Card>
        <CardHeader title="Entities" subtitle={`${entities.length} recent`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {entities.map((e) => (
            <div key={String(e.entity_id)}>
              {String(e.kind)} · {String(e.label)?.slice(0, 60)} · conf {String(e.confidence)}
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
