"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function LiveEngineeringPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "live-engineering"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/live-engineering"),
    refetchInterval: 7000,
  });
  const le = (data?.live_engineering as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Engineering Mode</h2>
      <Card>
        <CardHeader title="Repository" subtitle={String(le.repo || "none")} />
        <CardBody><p className="text-xs text-slate-400">IDE + terminal + git context fusion with supervised patch hints.</p></CardBody>
      </Card>
    </div>
  );
}
