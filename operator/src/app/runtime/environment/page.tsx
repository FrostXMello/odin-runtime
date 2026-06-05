"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeEnvironmentPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "environment"],
    queryFn: () => apiFetch<{ alerts: Array<Record<string, unknown>> }>("/runtime/environment"),
    refetchInterval: 5000,
  });
  const alerts = data?.alerts ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Environmental awareness</h2>
      <Card>
        <CardHeader title="Alerts" subtitle={`${alerts.length} active`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {alerts.map((a, i) => (
            <div key={i}>
              [{String(a.severity)}] {String(a.kind)}: {String(a.message)?.slice(0, 80)}
            </div>
          ))}
          {!alerts.length && <div>No alerts</div>}
        </CardBody>
      </Card>
    </div>
  );
}
