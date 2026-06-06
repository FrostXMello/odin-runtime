"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function WorkflowsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "workflows"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/workflows"),
    refetchInterval: 10000,
  });
  const w = (data?.workflows as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Engineering Workflows</h2>
      <Card>
        <CardHeader title="Issues & milestones" subtitle={`${String(w.issues ?? 0)} issues tracked`} />
        <CardBody className="text-xs text-slate-400">Sprint memory, goals, and implementation sequencing</CardBody>
      </Card>
    </div>
  );
}
