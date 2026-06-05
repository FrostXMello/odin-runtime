"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardHeader } from "@/components/ui/card";

export default function KnowledgeWorkspacePage() {
  const { data } = useQuery({ queryKey: ["runtime", "knowledge-workspace"], queryFn: () => apiFetch("/runtime/knowledge-workspace") });
  const w = (data?.workspace as Record<string, unknown>) ?? {};
  const g = (w.graph as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Knowledge workspace</h2>
      <Card><CardHeader title="Knowledge graph" subtitle={`${String(g.nodes ?? 0)} nodes`} /></Card>
    </div>
  );
}
