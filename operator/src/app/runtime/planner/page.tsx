"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RuntimePlannerPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "planner"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/planner"),
    refetchInterval: 4000,
  });

  const missions = (data?.missions as Record<string, Record<string, unknown>>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Semantic planner</h2>
      <Badge variant="default">{String(data?.active_plans ?? 0)} active plans</Badge>
      <Card>
        <CardHeader title="Mission plans" subtitle="confidence · strategy" />
        <CardBody className="space-y-2 text-xs font-mono text-slate-400">
          {Object.entries(missions).map(([id, m]) => (
            <div key={id} className="rounded border border-odin-border/60 px-3 py-2">
              <span className="text-odin-cyan">{id.slice(0, 12)}…</span>
              <span className="ml-2">
                conf {JSON.stringify(m.confidence)} · {String((m.strategy as Record<string, unknown>)?.kind ?? "—")}
              </span>
            </div>
          ))}
          {!Object.keys(missions).length && <p>No active semantic plans.</p>}
        </CardBody>
      </Card>
    </div>
  );
}
