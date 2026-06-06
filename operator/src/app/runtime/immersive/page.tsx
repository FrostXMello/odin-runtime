"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ImmersivePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "immersive"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/immersive"),
    refetchInterval: 6000,
  });
  const im = (data?.immersive as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Immersive Cognitive UI</h2>
      <Card>
        <CardHeader title="Mode" subtitle={String(im.mode ?? "balanced")} />
        <CardBody><p className="text-xs text-slate-400">GPU-safe caps for GTX 1650 Ti — minimal to cinematic.</p></CardBody>
      </Card>
    </div>
  );
}
