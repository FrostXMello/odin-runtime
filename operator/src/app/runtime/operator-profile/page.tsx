"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeOperatorProfilePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "operator-profile"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/operator-profile"),
    refetchInterval: 8000,
  });
  const op = (data?.operator as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Operator profile</h2>
      <Card>
        <CardHeader title="Collaboration" subtitle={`Style: ${String(op.style ?? "balanced")}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Interactions: {String(op.recent_interactions ?? 0)} | Transparent assistance
        </CardBody>
      </Card>
    </div>
  );
}
