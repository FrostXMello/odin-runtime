"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeSafetyPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "safety"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/safety"),
    refetchInterval: 5000,
  });
  const interventions = (data?.interventions as Array<Record<string, unknown>>) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Autonomy safety</h2>
      <Card>
        <CardHeader title="Interventions" subtitle={`Throttle remaining: ${String(data?.throttle_remaining ?? "—")}`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {interventions.map((v, i) => (
            <div key={i}>
              {String(v.kind)}: {String(v.reason ?? v.message ?? JSON.stringify(v)).slice(0, 80)}
            </div>
          ))}
          {!interventions.length && <div>No recent interventions</div>}
        </CardBody>
      </Card>
    </div>
  );
}
