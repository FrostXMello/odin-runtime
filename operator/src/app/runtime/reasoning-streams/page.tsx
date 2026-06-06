"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ReasoningStreamsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "reasoning-streams"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/reasoning-streams"),
    refetchInterval: 5000,
  });
  const streams = (data?.streams as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Visual Reasoning Streams</h2>
      <Card>
        <CardHeader title="Stream items" subtitle={String(streams.items ?? 0)} />
        <CardBody><p className="text-xs text-slate-400">Explainable cognitive chains — transparent, non-deceptive.</p></CardBody>
      </Card>
    </div>
  );
}
