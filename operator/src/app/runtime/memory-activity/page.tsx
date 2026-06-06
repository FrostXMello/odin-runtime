"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function MemoryActivityPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "memory-activity"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/memory-activity"),
    refetchInterval: 8000,
  });
  const mem = (data?.memory_activity as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Memory Activity Map</h2>
      <Card>
        <CardHeader title="Threads" subtitle={String(mem.threads ?? 0)} />
        <CardBody>
          <p className="text-xs text-slate-400">Active cells: {String(mem.active_cells ?? 0)}</p>
        </CardBody>
      </Card>
    </div>
  );
}
