"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ModelRoutingPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "model-routing"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/model-routing"),
    refetchInterval: 10000,
  });
  const orch = (data?.orchestration as Record<string, unknown>) ?? {};
  const ai = (data?.local_ai as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Model Routing</h2>
      <Card>
        <CardHeader title="Orchestration" subtitle={`${String(orch.routes ?? 0)} routes · mode ${String(ai.inference_mode ?? "—")}`} />
        <CardBody className="text-xs text-slate-400">Adaptive model selection for 4GB VRAM daily-driver hardware</CardBody>
      </Card>
    </div>
  );
}
