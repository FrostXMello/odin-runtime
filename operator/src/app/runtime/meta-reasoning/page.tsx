"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeMetaReasoningPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "meta-reasoning"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/meta-reasoning"),
    refetchInterval: 8000,
  });
  const meta = (data?.meta as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Meta-reasoning</h2>
      <Card>
        <CardHeader title="Self-analysis" subtitle={`Analyses: ${String(meta.analysis_count ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Calibration, hallucination review, drift detection</CardBody>
      </Card>
    </div>
  );
}
