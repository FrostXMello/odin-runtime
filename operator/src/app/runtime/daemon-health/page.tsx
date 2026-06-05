"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function DaemonHealthPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "daemon"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/daemon"),
    refetchInterval: 5000,
  });
  const d = (data?.daemon as Record<string, unknown>) ?? {};
  const hb = (d.heartbeat as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Daemon health</h2>
      <Card>
        <CardHeader title="Uptime" subtitle={`${String(d.uptime_s ?? 0)}s`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Heartbeats: {String(hb.count ?? 0)} · Idle: {String(d.idle)}
        </CardBody>
      </Card>
    </div>
  );
}
