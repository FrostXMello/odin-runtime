"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function DaemonPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "daemon"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/daemon"),
    refetchInterval: 8000,
  });
  const d = (data?.daemon as Record<string, unknown>) ?? {};
  const start = useMutation({
    mutationFn: () => apiFetch("/runtime/daemon/start", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "daemon"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Daemon mode</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => start.mutate()}>Start daemon</button>
      <Card>
        <CardHeader title="Status" subtitle={d.started_at ? "Running" : "Stopped"} />
        <CardBody className="font-mono text-xs text-slate-400">Persistent background cognition</CardBody>
      </Card>
    </div>
  );
}
