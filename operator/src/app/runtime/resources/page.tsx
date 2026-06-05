"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ResourcesPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "resources"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/resource-optimization"),
    refetchInterval: 5000,
  });
  const res = (data?.resources as Record<string, unknown>) ?? {};
  const optimize = useMutation({
    mutationFn: () => apiFetch("/runtime/resource-optimization/optimize", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "resources"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Resource dashboard</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => optimize.mutate()}>Optimize</button>
      <Card>
        <CardHeader title="Hardware" subtitle={`VRAM: ${String(res.vram_mb ?? 0)}MB | RAM: ${String(res.ram_mb ?? 0)}MB`} />
        <CardBody className="font-mono text-xs text-slate-400">Mode: {String(res.mode ?? "normal")}</CardBody>
      </Card>
    </div>
  );
}
