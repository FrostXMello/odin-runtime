"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ModelInspectorPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "local-ai"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/local-ai"),
    refetchInterval: 5000,
  });
  const ai = (data?.local_ai as Record<string, unknown>) ?? {};
  const gpu = (ai.gpu as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Model runtime inspector</h2>
      <Card>
        <CardHeader title="Active model" subtitle={String(ai.active_model ?? "none")} />
        <CardBody className="font-mono text-xs text-slate-400">
          Provider: {String(ai.provider ?? "—")} | Loaded: {String((ai.loaded as unknown[])?.length ?? 0)}
          <br />VRAM: {String(gpu.vram_mb ?? 0)}MB
        </CardBody>
      </Card>
    </div>
  );
}
