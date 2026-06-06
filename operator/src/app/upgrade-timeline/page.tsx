"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "upgrade-timeline"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/evolution-review"),
    refetchInterval: 12000,
  });
  const review = (data?.evolution_review as Record<string, unknown>) ?? {};
  const timeline = (review?.timeline as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Upgrade Timeline</h2>
      <Card>
        <CardHeader title="Architecture evolution" subtitle="supervised history" />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(timeline, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
