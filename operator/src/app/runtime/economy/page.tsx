"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeEconomyPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "economy"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/economy"),
    refetchInterval: 8000,
  });
  const econ = (data?.economy as Record<string, unknown>) ?? {};
  const budget = (econ.budget as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Cognitive economy</h2>
      <Card>
        <CardHeader title="Budget" subtitle={`Mode: ${String(budget.mode ?? "balanced")}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Remaining: {String(budget.remaining ?? 0)} | Model: {String(econ.selected_model ?? "—")}
        </CardBody>
      </Card>
    </div>
  );
}
