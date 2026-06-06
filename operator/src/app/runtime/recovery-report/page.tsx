"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RecoveryReportPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "recovery-report"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/recovery-report"),
    refetchInterval: 10000,
  });
  const report = (data?.report as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Recovery Report</h2>
      <Card>
        <CardHeader title="Status" subtitle={String(report.status ?? "unknown")} />
        <CardBody className="text-xs text-slate-400">Automatic checkpoint validation and safe-mode recovery</CardBody>
      </Card>
    </div>
  );
}
