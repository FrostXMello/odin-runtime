"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function IntelligencePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "intelligence"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/intelligence"),
    refetchInterval: 10000,
  });
  const evaluate = useMutation({
    mutationFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/intelligence/evaluate", {
        method: "POST",
        body: { text: "Evaluate reasoning quality", steps: ["analyze", "conclude"] },
      }),
  });
  const q = (data?.quality as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Intelligence Quality</h2>
      <Card>
        <CardHeader title="Chain tracker" subtitle={String((q.chains as Record<string, unknown>)?.trend ?? "—")} />
        <CardBody>
          <button type="button" className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => evaluate.mutate()}>
            Score sample reasoning
          </button>
        </CardBody>
      </Card>
    </div>
  );
}
