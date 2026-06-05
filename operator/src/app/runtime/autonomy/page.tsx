"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeAutonomyPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "autonomy"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/autonomy"),
    refetchInterval: 5000,
  });
  const state = (data?.state as Record<string, unknown>) ?? {};
  const metrics = (data?.metrics as Record<string, number>) ?? {};

  const start = useMutation({
    mutationFn: () => apiFetch("/runtime/autonomy/start", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "autonomy"] }),
  });
  const pause = useMutation({
    mutationFn: () => apiFetch("/runtime/autonomy/pause", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "autonomy"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Autonomous operator</h2>
      <div className="flex gap-2">
        <button
          className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
          onClick={() => start.mutate()}
        >
          Start
        </button>
        <button
          className="rounded bg-odin-border px-3 py-1 text-xs text-slate-300"
          onClick={() => pause.mutate()}
        >
          Pause
        </button>
      </div>
      <Card>
        <CardHeader title="Loop status" subtitle={`State: ${String(state.run_state ?? "—")}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Mode: {String(state.mode)}</div>
          <div>Cycles: {String(state.cycle_count ?? 0)}</div>
          <div>Missions generated: {String(metrics.missions_spawned ?? 0)}</div>
          <div>Safety interventions: {String(metrics.safety_interventions ?? 0)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
