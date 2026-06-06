"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function LiveCopilotPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "live-copilot"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/live-copilot"),
    refetchInterval: 8000,
  });
  const lc = (data?.live_copilot as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Copilot</h2>
      <Card>
        <CardHeader title="Mode" subtitle={String(lc.mode ?? "suggestive")} />
        <CardBody className="text-xs text-slate-400">Real-time engineering assistance with supervised-action mode</CardBody>
      </Card>
    </div>
  );
}
