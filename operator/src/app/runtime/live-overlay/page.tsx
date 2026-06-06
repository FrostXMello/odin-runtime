"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function LiveOverlayPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "live-overlay"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/live-overlay"),
    refetchInterval: 7000,
  });
  const overlay = (data?.overlay as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Workspace Overlay</h2>
      <Card>
        <CardHeader title="Mode" subtitle={String(overlay.mode ?? "assistant")} />
        <CardBody>
          <p className="text-xs text-slate-400">Passive · Assistant · Engineering · Debugging · Strategic</p>
        </CardBody>
      </Card>
    </div>
  );
}
