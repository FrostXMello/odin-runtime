"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeResearchFabricPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "research-fabric"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/research"),
    refetchInterval: 8000,
  });

  const start = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/research/start", {
        method: "POST",
        body: JSON.stringify({ topic: "local AI orchestration" }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "research-fabric"] }),
  });

  const sessions = (data?.sessions as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Research fabric</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => start.mutate()}
      >
        Start research
      </button>
      <Card>
        <CardHeader title="Active research" subtitle={`Sessions: ${sessions.length}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Enabled: {String(data?.enabled ?? false)}
        </CardBody>
      </Card>
    </div>
  );
}
