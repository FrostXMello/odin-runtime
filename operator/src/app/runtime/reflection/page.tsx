"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeReflectionPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "reflection"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/reflection"),
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Self-critique & reflection</h2>
      <Card>
        <CardHeader title="Reflection guards" subtitle="Recursion limits" />
        <CardBody className="font-mono text-xs text-slate-400">
          <div>Max depth: {String(data?.max_depth ?? "—")}</div>
          <div>Time budget (s): {String(data?.time_budget_seconds ?? "—")}</div>
        </CardBody>
      </Card>
    </div>
  );
}
