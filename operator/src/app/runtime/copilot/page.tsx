"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function CopilotIntelPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "copilot-intel"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/copilot"),
    refetchInterval: 10000,
  });
  const cc = (data?.code_copilot as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Code Copilot</h2>
      <Card>
        <CardHeader title="Patches" subtitle={`${String(cc.patches_generated ?? 0)} generated`} />
        <CardBody className="text-xs text-slate-400">Repository reasoning, patch planning, and multi-file context</CardBody>
      </Card>
    </div>
  );
}
