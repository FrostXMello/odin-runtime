"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimePerformancePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "capability-performance"],
    queryFn: () =>
      apiFetch<{ capabilities: Record<string, Record<string, number>> }>(
        "/runtime/capability-performance"
      ),
    refetchInterval: 5000,
  });

  const caps = data?.capabilities ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Capability performance</h2>
      {Object.entries(caps).map(([name, m]) => (
        <Card key={name}>
          <CardHeader title={name} />
          <CardBody className="text-xs font-mono text-slate-400">
            reliability {(m.reliability * 100).toFixed(0)}% · fail rate {(m.failure_rate * 100).toFixed(0)}%
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
