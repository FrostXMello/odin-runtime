"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function PresencePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "presence"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/presence"),
    refetchInterval: 6000,
  });
  const pres = (data?.presence as Record<string, unknown>) ?? {};
  const emotion = (pres.emotion as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Embodied Presence</h2>
      <Card>
        <CardHeader title="Mood" subtitle={String(emotion.mood ?? "neutral")} />
        <CardBody>
          <p className="text-xs text-slate-400">Simulated emotional model — not consciousness.</p>
          <p className="mt-2 text-xs">Events: {String(pres.events ?? 0)}</p>
        </CardBody>
      </Card>
    </div>
  );
}
