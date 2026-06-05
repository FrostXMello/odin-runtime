"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeCopilotPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "copilot"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/copilot"),
    refetchInterval: 5000,
  });
  const suggestions = (data?.suggestions as unknown[]) ?? [];
  const predicted = (data?.predicted_next as string[]) ?? [];

  const tick = useMutation({
    mutationFn: () => apiFetch("/runtime/copilot/tick", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "copilot"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live copilot</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => tick.mutate()}
      >
        Generate suggestions
      </button>
      <Card>
        <CardHeader title="Copilot mode" subtitle={`Mode: ${String(data?.mode ?? "—")}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-2">
          <div>Suggestions: {suggestions.length}</div>
          <div>Predicted next: {predicted.join(" → ") || "—"}</div>
        </CardBody>
      </Card>
    </div>
  );
}
