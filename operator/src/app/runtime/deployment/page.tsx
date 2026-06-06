"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function DeploymentPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "deployment"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/deployment"),
    refetchInterval: 15000,
  });
  const d = (data?.deployment as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Deployment</h2>
      <Card>
        <CardHeader title="Runtime profile" subtitle={String(d.profile ?? "unknown")} />
        <CardBody className="text-xs text-slate-400">
          Platform: {String(d.platform ?? "—")} · Bootstrapped: {String(d.bootstrapped ?? false)} · Snapshots:{" "}
          {String(d.snapshots ?? 0)}
        </CardBody>
      </Card>
    </div>
  );
}
