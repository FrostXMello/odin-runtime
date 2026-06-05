"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeWorldModelPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "world-model"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/world-model"),
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">World model</h2>
      <Card>
        <CardHeader title="World state" subtitle={`Entities: ${String(data?.entity_count ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Updated: {String(data?.updated_at ?? "—")}
        </CardBody>
      </Card>
    </div>
  );
}
