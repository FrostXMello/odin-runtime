"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeDelegationPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "delegation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/society/delegation"),
    refetchInterval: 8000,
  });
  const delegations = (data?.delegations as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Delegation</h2>
      <Card>
        <CardHeader title="Active delegations" subtitle={`${delegations.length} total`} />
        <CardBody className="font-mono text-xs text-slate-400">
          {delegations.length === 0 ? "No delegations" : `${delegations.length} delegation(s)`}
        </CardBody>
      </Card>
    </div>
  );
}
