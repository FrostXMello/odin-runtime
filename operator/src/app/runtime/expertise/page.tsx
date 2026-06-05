"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeExpertisePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "expertise"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/society/expertise"),
    refetchInterval: 10000,
  });
  const heatmap = (data?.heatmap as Record<string, number>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Expertise</h2>
      <Card>
        <CardHeader title="Expertise heatmap" subtitle={`${Object.keys(heatmap).length} domains`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          {Object.keys(heatmap).length === 0 ? (
            <div>No expertise recorded</div>
          ) : (
            Object.entries(heatmap).map(([k, v]) => (
              <div key={k}>
                {k}: {String(v)}
              </div>
            ))
          )}
        </CardBody>
      </Card>
    </div>
  );
}
