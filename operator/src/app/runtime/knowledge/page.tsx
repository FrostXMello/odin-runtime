"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeKnowledgePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "knowledge"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/knowledge"),
    refetchInterval: 8000,
  });
  const nodes = (data?.nodes as unknown[]) ?? [];
  const snap = (data?.snapshot as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Knowledge fabric</h2>
      <Card>
        <CardHeader title="Knowledge graph" subtitle={`Nodes: ${nodes.length}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Enabled: {String(snap.enabled ?? false)}</div>
          <div>Entities: {String((snap.graph as Record<string, unknown>)?.entity_count ?? 0)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
