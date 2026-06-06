"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "reasoning-live-render"],
    queryFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/reasoning-live/render", {
        method: "POST",
        body: JSON.stringify({ thought: "attention map" }),
      }),
    refetchInterval: 9000,
  });
  const heatmap = (data?.heatmap as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Attention Map</h2>
      <Card>
        <CardHeader title="Confidence heatmap" subtitle="live reasoning layers" />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(heatmap, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
