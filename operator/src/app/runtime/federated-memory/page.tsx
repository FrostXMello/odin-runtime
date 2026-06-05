"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeFederatedMemoryPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "federated-memory"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/federated-memory"),
    refetchInterval: 8000,
  });
  const memories = (data?.memories as unknown[]) ?? [];

  const share = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/federated-memory/share", {
        method: "POST",
        body: JSON.stringify({ from_node: "local", fact: "validated strategy pattern", confidence: 0.8, trust: 0.6 }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "federated-memory"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Federated memory</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => share.mutate()}
      >
        Share knowledge
      </button>
      <Card>
        <CardHeader title="Shared memories" subtitle={`Count: ${memories.length}`} />
        <CardBody className="font-mono text-xs text-slate-400">Trust-weighted, lineage-tracked</CardBody>
      </Card>
    </div>
  );
}
