"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeResourcesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "resources"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/resources"),
    refetchInterval: 5000,
  });
  const ram = (data?.ram as Record<string, unknown>) ?? {};
  const gpu = (data?.gpu as Record<string, unknown>) ?? {};
  const loaded = (data?.loaded as string[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Model resources</h2>
      <Card>
        <CardHeader title="Memory pressure" subtitle={`${Math.round(Number(data?.memory_pressure ?? 0) * 100)}%`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>RAM available: {String(ram.available_mb)} MB</div>
          <div>GPU detected: {String(gpu.gpu_detected)}</div>
          <div>Loaded models: {loaded.join(", ") || "none"}</div>
        </CardBody>
      </Card>
    </div>
  );
}
