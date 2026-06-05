"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeOverlayPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "overlay"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/overlay"),
    refetchInterval: 2000,
  });
  const annotations = (data?.annotations as unknown[]) ?? [];
  const status = (data?.status as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Execution overlay</h2>
      <Card>
        <CardHeader title="Live overlay" subtitle={`Enabled: ${String(data?.enabled ?? false)}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Status: {String(status.status ?? "idle")}</div>
          <div>Annotations: {annotations.length}</div>
          <div>Cursor: {JSON.stringify(data?.cursor ?? null)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
