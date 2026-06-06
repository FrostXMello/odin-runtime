"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function DiagnosticsPanelPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "diagnostics-panel"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/diagnostics"),
    refetchInterval: 10000,
  });
  const report = (data?.report as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Diagnostics</h2>
      <Card>
        <CardHeader title="Runtime health" subtitle={String(report.status ?? "unknown")} />
        <CardBody className="text-xs text-slate-400">Guardian, self-healing, and daemon supervision snapshot</CardBody>
      </Card>
    </div>
  );
}
