"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeWorldPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "world"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/world"),
    refetchInterval: 8000,
  });
  const world = (data?.world as Record<string, unknown>) ?? {};
  const entities = (world.entities as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">World model</h2>
      <Card>
        <CardHeader title="Entities" subtitle={`Count: ${entities.length}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Relationships: {String((world.relationships as unknown[])?.length ?? 0)}
        </CardBody>
      </Card>
    </div>
  );
}
