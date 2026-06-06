"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ArchitecturePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "architecture"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/architecture"),
    refetchInterval: 15000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Architecture</h2>
      <Card>
        <CardHeader title="Drift detection" subtitle="Repository topology and service relationships" />
        <CardBody className="text-xs text-slate-400">Architecture memory and drift viewer</CardBody>
      </Card>
    </div>
  );
}
