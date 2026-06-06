"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ReasoningPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "reasoning"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/reasoning"),
    refetchInterval: 10000,
  });
  const routing = (data?.routing as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Reasoning</h2>
      <Card>
        <CardHeader title="Model routes" subtitle={`${String(routing.routes ?? 0)} routed`} />
        <CardBody className="text-xs text-slate-400">Live reasoning chain quality and routing overlay</CardBody>
      </Card>
    </div>
  );
}
