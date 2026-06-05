"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeIdentityPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "identity"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/identity"),
    refetchInterval: 15000,
  });
  const behavioral = (data?.behavioral as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Agent identity</h2>
      <Card>
        <CardHeader title="Behavioral profile" subtitle={`v${String(data?.version ?? 1)}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Style: {String(behavioral.reasoning_style)}</div>
          <div>Verbosity: {String(behavioral.verbosity)}</div>
          <div>Planning aggressiveness: {String(behavioral.planning_aggressiveness)}</div>
          <div>Risk tolerance: {String(behavioral.risk_tolerance)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
