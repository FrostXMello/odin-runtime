"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function WorkflowIntelligencePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "workflow-intelligence"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/workflow-intelligence"),
    refetchInterval: 15000,
  });
  const pred = (data?.prediction as Record<string, unknown>) ?? {};
  const hint = (pred.hint as string) ?? "";
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Workflow Intelligence</h2>
      <Card>
        <CardHeader title="Prediction" subtitle={hint || "Learning operator patterns"} />
        <CardBody className="text-xs text-slate-400">Productivity patterns and proactive assistance</CardBody>
      </Card>
    </div>
  );
}
