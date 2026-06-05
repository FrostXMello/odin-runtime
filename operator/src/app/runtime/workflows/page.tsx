"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeWorkflowsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "workflows"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/workflows"),
    refetchInterval: 5000,
  });
  const macros = (data?.macros as unknown[]) ?? [];
  const recorder = (data?.recorder as Record<string, unknown>) ?? {};

  const recordStart = useMutation({
    mutationFn: () => apiFetch("/runtime/workflows/record/start", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "workflows"] }),
  });
  const recordStop = useMutation({
    mutationFn: () => apiFetch("/runtime/workflows/record/stop", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "workflows"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Workflow macros</h2>
      <div className="flex gap-2">
        <button
          className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
          onClick={() => recordStart.mutate()}
        >
          Start recording
        </button>
        <button
          className="rounded bg-odin-border px-3 py-1 text-xs text-slate-300"
          onClick={() => recordStop.mutate()}
        >
          Stop recording
        </button>
      </div>
      <Card>
        <CardHeader title="Recorder" subtitle={`Recording: ${String(recorder.recording ?? false)}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Macros: {macros.length}
        </CardBody>
      </Card>
    </div>
  );
}
