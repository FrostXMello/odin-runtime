"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ArchitectureHistoryPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "architecture-history"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/architecture-history"),
    refetchInterval: 20000,
  });
  const timeline = (data?.timeline as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Architecture History</h2>
      <Card>
        <CardHeader title="Decisions" subtitle={`${timeline.length} entries`} />
        <CardBody>
          <ul className="space-y-1 text-xs text-slate-300">
            {timeline.slice(0, 6).map((d, i) => (
              <li key={i}>{String((d as Record<string, unknown>).title ?? "")}</li>
            ))}
          </ul>
        </CardBody>
      </Card>
    </div>
  );
}
