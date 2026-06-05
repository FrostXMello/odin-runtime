"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeContinuityPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "continuity"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/continuity"),
    refetchInterval: 8000,
  });
  const c = (data?.continuity as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Runtime continuity</h2>
      <Card>
        <CardHeader title="Sessions" subtitle={`Active: ${String(c.active_sessions ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Deferred: {String(c.deferred_cognition ?? 0)} | Context windows: {String(c.context_windows ?? 0)}
        </CardBody>
      </Card>
    </div>
  );
}
