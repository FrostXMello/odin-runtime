"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeSourcesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "sources"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/sources"),
    refetchInterval: 10000,
  });
  const sources = (data?.sources as unknown[]) ?? [];
  const gov = (data?.governance as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Sources</h2>
      <Card>
        <CardHeader title="Source lineage" subtitle={`${sources.length} sources`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Budget used: {String(gov.budget_used ?? 0)}</div>
          <div>Read-only: {String(gov.web_read_only ?? true)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
