"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ResourceSurvivalPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "resources"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/resource-optimization"),
    refetchInterval: 8000,
  });
  const r = (data?.resources as Record<string, unknown>) ?? {};
  const survive = useMutation({
    mutationFn: () => apiFetch("/runtime/resource-optimization/survive", { method: "POST", body: JSON.stringify({ mode: "ultra_light" }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "resources"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Resource survival</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => survive.mutate()}>Ultra-light mode</button>
      <Card>
        <CardHeader title="VRAM budget" subtitle={`${String(r.vram_mb ?? 0)} MB`} />
        <CardBody className="text-xs text-slate-400">Survival: {String(r.survival_mode ?? "balanced")}</CardBody>
      </Card>
    </div>
  );
}
