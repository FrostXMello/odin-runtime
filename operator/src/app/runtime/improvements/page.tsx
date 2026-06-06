"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ImprovementsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "improvements"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/improvements"),
    refetchInterval: 10000,
  });
  const backlog = (data?.backlog as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Improvement Backlog</h2>
      <Card>
        <CardHeader title="Proposals" subtitle={`${backlog.length} items`} />
        <CardBody>
          <ul className="space-y-1 text-xs text-slate-300">
            {backlog.slice(0, 8).map((item, i) => (
              <li key={i}>{String((item as Record<string, unknown>).title ?? "")}</li>
            ))}
          </ul>
        </CardBody>
      </Card>
    </div>
  );
}
