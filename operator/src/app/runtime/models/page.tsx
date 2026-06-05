"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeModelsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "models"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/models"),
    refetchInterval: 8000,
  });
  const registry = (data?.registry as Record<string, unknown>) ?? {};
  const models = (registry.models as Array<Record<string, unknown>>) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Local model runtime</h2>
      <Card>
        <CardHeader title="Registry" subtitle={`Provider: ${String(data?.provider ?? "—")}`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {models.map((m) => (
            <div key={String(m.name)}>
              {String(m.name)} · {String(m.provider)} · ctx {String(m.context_window)} · loaded{" "}
              {String(m.loaded)}
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
