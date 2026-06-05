"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeStrategiesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "strategies"],
    queryFn: () =>
      apiFetch<{
        strategies: Array<{
          mission_id: string;
          strategy: Record<string, unknown>;
          confidence: Record<string, number>;
        }>;
      }>("/runtime/strategies"),
    refetchInterval: 4000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Execution strategies</h2>
      {(data?.strategies ?? []).map((s) => (
        <Card key={s.mission_id}>
          <CardHeader title={s.mission_id.slice(0, 14)} subtitle={String(s.strategy?.kind ?? s.strategy)} />
          <CardBody className="font-mono text-xs text-slate-400">
            confidence: {JSON.stringify(s.confidence)}
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
