"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ReasoningMapPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "reasoning-map"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/reasoning-map"),
    refetchInterval: 6000,
  });
  const map = (data?.reasoning_map as Record<string, unknown>) ?? {};
  const layers = (map.layers as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Reasoning Map</h2>
      <Card>
        <CardHeader title="Layers" subtitle={`${layers.length} steps`} />
        <CardBody>
          <ul className="space-y-1 text-xs text-slate-300">
            {layers.map((l, i) => (
              <li key={i}>{String((l as Record<string, unknown>).label ?? "")}</li>
            ))}
          </ul>
        </CardBody>
      </Card>
    </div>
  );
}
