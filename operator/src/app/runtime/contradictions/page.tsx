"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeContradictionsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "contradictions"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/contradictions"),
    refetchInterval: 10000,
  });
  const items = (data?.contradictions as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Contradictions</h2>
      <Card>
        <CardHeader title="Contradiction explorer" subtitle={`${items.length} detected`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          {items.length === 0 ? (
            <div>No contradictions detected</div>
          ) : (
            items.map((c, i) => {
              const item = c as Record<string, unknown>;
              return <div key={i}>{String(item.entity)}: conflict detected</div>;
            })
          )}
        </CardBody>
      </Card>
    </div>
  );
}
