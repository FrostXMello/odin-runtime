"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function StabilityPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "stability"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/stability"),
    refetchInterval: 8000,
  });
  const s = (data?.stability as Record<string, unknown>) ?? {};
  const supervise = useMutation({
    mutationFn: () => apiFetch("/runtime/stability/supervise", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "stability"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Runtime stability</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => supervise.mutate()}>Supervise</button>
      <Card>
        <CardHeader title="Guardian" subtitle={String(s.mode ?? "normal")} />
        <CardBody className="font-mono text-xs text-slate-400">
          Degraded: {String(s.degraded)} · Recoveries: {String(s.recoveries)}
        </CardBody>
      </Card>
    </div>
  );
}
