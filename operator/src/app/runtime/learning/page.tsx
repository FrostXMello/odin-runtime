"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeLearningPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "learning"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/learning"),
    refetchInterval: 5000,
  });
  const stats = (data?.strategy_stats as Record<string, Record<string, number>>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Learning runtime</h2>
      <p className="text-xs text-odin-muted">Cycles: {String(data?.improvement_cycles ?? 0)}</p>
      <Card>
        <CardHeader title="Strategy performance" />
        <CardBody className="font-mono text-xs text-slate-400">
          {Object.entries(stats).map(([k, v]) => (
            <div key={k}>
              {k}: success {(v.success_rate * 100).toFixed(0)}% · attempts {v.attempts}
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
