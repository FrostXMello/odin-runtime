"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "mission-playback"],
    queryFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/reasoning-live/render", {
        method: "POST",
        body: JSON.stringify({ thought: "mission playback" }),
      }),
    refetchInterval: 10000,
  });
  const playback = (data?.playback as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Mission Playback</h2>
      <Card>
        <CardHeader title="Cognition timeline" subtitle={`${playback.length} events`} />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(playback, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
