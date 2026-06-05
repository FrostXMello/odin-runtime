"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeObjectivesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "objectives"],
    queryFn: () => apiFetch<{ objectives: Array<Record<string, unknown>> }>("/runtime/objectives"),
    refetchInterval: 8000,
  });
  const objs = data?.objectives ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Persistent objectives</h2>
      <Card>
        <CardHeader title="Objective graph" subtitle={`${objs.length} objectives`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {objs.map((o) => (
            <div key={String(o.objective_id)}>
              {String(o.title)} · p={String(o.priority)} · conf={String(o.confidence)} ·{" "}
              {String(o.status)}
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
