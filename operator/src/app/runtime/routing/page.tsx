"use client";

import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RuntimeRoutingPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "routing"],
    queryFn: () => runtimeApi.routing(),
    refetchInterval: 3000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Capability routing</h2>
      <Card>
        <CardHeader title="Eligible targets" subtitle="load-balanced workers" />
        <CardBody className="space-y-2">
          {(data?.targets ?? []).map((t) => (
            <div
              key={String(t.worker_id)}
              className="flex items-center justify-between rounded border border-odin-border/60 px-3 py-2 text-xs"
            >
              <span className="font-mono">{String(t.worker_id)}</span>
              <Badge variant={t.stale ? "critical" : "healthy"}>
                score {String(t.score ?? 0)}
              </Badge>
            </div>
          ))}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Recent decisions" />
        <CardBody className="font-mono text-xs text-slate-400">
          {(data?.recent_decisions ?? []).slice(-20).reverse().map((d, i) => (
            <div key={i}>
              {String(d.capability)} → {String(d.worker_id ?? "none")} (score {String(d.score)})
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
