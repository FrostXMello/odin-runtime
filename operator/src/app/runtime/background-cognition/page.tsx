"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeBackgroundCognitionPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "background-cognition"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/background-cognition"),
    refetchInterval: 8000,
  });
  const bg = (data?.background as Record<string, unknown>) ?? {};
  const run = useMutation({
    mutationFn: () => apiFetch("/runtime/background-cognition/run", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "background-cognition"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Background cognition</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => run.mutate()}>Run cycle</button>
      <Card>
        <CardHeader title="Idle processing" subtitle={`Consolidations: ${String(bg.consolidation_history ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Low priority, bounded, cancellable</CardBody>
      </Card>
    </div>
  );
}
