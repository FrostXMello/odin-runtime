"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function AutomationLivePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "automation-live"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/automation-live"),
    refetchInterval: 8000,
  });
  const a = (data?.automation as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Automation live</h2>
      <Card>
        <CardHeader title="Mode" subtitle={String(a.mode ?? "simulation")} />
        <CardBody className="text-xs text-slate-400">Verifications: {String(a.verifications ?? 0)}</CardBody>
      </Card>
    </div>
  );
}
