"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ContinuityPanelPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "continuity-panel"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/continuity"),
    refetchInterval: 10000,
  });
  const c = (data?.continuity as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Cognitive Continuity</h2>
      <Card>
        <CardHeader title="Memory threads" subtitle={`${String(c.threads ?? 0)} threads · ${String(c.unfinished ?? 0)} unfinished`} />
        <CardBody className="text-xs text-slate-400">Long-horizon engineering continuity explorer</CardBody>
      </Card>
    </div>
  );
}
