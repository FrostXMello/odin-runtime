"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function SelfHealingPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "self-healing"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/self-healing"),
    refetchInterval: 10000,
  });
  const h = (data?.self_healing as Record<string, unknown>) ?? {};
  const heal = useMutation({
    mutationFn: () => apiFetch("/runtime/self-healing/heal", { method: "POST", body: JSON.stringify({}) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "self-healing"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Self-healing</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => heal.mutate()}>Heal executions</button>
      <Card>
        <CardHeader title="Repairs" subtitle={`${String(h.repairs ?? 0)} repairs`} />
        <CardBody className="text-xs text-slate-400">Salvages: {String(h.salvages ?? 0)}</CardBody>
      </Card>
    </div>
  );
}
