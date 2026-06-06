"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function CognitiveDaemonPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "cognitive-daemon"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognitive-daemon"),
    refetchInterval: 10000,
  });
  const daemon = (data?.daemon as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Cognitive Daemon</h2>
      <Card>
        <CardHeader title="Mode" subtitle={String(daemon.mode ?? "desktop_assistant")} />
        <CardBody>
          <p className="text-xs text-slate-400">Uptime: {String(daemon.uptime_s ?? 0)}s · Bounded background cognition</p>
        </CardBody>
      </Card>
    </div>
  );
}
