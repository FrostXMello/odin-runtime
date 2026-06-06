"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function EngineeringPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "engineering"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/engineering"),
    refetchInterval: 10000,
  });
  const mem = (data?.memory as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Engineering Workspace</h2>
      <Card>
        <CardHeader title="Engineering memory" subtitle={`${String(mem.repos ?? 0)} repos · ${String(mem.bugs ?? 0)} bugs tracked`} />
        <CardBody className="text-xs text-slate-400">Long-term repository cognition and technical decisions</CardBody>
      </Card>
    </div>
  );
}
