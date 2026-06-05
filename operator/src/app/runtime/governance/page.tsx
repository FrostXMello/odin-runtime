"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeGovernancePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "governance"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/governance"),
    refetchInterval: 8000,
  });
  const gov = (data?.governance as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Federation governance</h2>
      <Card>
        <CardHeader title="Trust & quarantine" subtitle={`Quarantined: ${String((gov.quarantined as unknown[])?.length ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Shutdown: {String(gov.shutdown ?? false)}</div>
          <div>Policies: {String((gov.policies as unknown[])?.length ?? 0)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
