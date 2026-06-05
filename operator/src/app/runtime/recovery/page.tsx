"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeRecoveryPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "recovery"],
    queryFn: () => apiFetch<{ metrics: Record<string, number> }>("/runtime/recovery"),
    refetchInterval: 5000,
  });
  const run = useMutation({
    mutationFn: () => apiFetch<Record<string, unknown>>("/runtime/recovery/run", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "recovery"] }),
  });
  const m = data?.metrics ?? {};
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-medium text-slate-200">Recovery</h2>
        <button
          type="button"
          className="rounded border border-odin-border px-2 py-1 text-xs text-odin-cyan hover:bg-odin-cyan/10"
          onClick={() => run.mutate()}
          disabled={run.isPending}
        >
          Run recovery
        </button>
      </div>
      <Card>
        <CardHeader title="Recovery metrics" />
        <CardBody className="grid gap-2 sm:grid-cols-3 font-mono text-xs text-slate-400">
          {Object.entries(m).map(([k, v]) => (
            <div key={k}>
              {k}: {v}
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
