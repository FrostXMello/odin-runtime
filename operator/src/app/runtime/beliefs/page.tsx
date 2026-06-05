"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeBeliefsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "beliefs"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/beliefs"),
    refetchInterval: 8000,
  });
  const beliefs = (data?.beliefs as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Belief state</h2>
      <Card>
        <CardHeader title="Beliefs" subtitle={`${beliefs.length} tracked`} />
        <CardBody className="font-mono text-xs text-slate-400">
          {beliefs.length === 0 ? "No beliefs yet" : `${beliefs.length} belief entries`}
        </CardBody>
      </Card>
    </div>
  );
}
