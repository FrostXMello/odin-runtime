"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ContextPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "context"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/context"),
    refetchInterval: 8000,
  });
  const fusion = (data?.fusion as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Active Context</h2>
      <Card>
        <CardHeader title="Fusion graph" subtitle={`nodes ${String((fusion.attention as Record<string, unknown>)?.nodes ?? 0)}`} />
        <CardBody className="text-xs text-slate-400">IDE + terminal + browser context merge</CardBody>
      </Card>
    </div>
  );
}
