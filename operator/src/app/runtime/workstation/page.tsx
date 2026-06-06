"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function WorkstationPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "workstation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/workstation"),
    refetchInterval: 8000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Cognitive Workstation</h2>
      <Card>
        <CardHeader title="Workstation state" subtitle="Local-only awareness" />
        <CardBody className="text-xs text-slate-400">Context fusion, attention, and continuity diagnostics</CardBody>
      </Card>
    </div>
  );
}
