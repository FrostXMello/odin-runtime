"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function AttentionPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "attention"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/attention"),
    refetchInterval: 8000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Attention</h2>
      <Card>
        <CardHeader title="Active focus" subtitle="Workstation attention viewer" />
        <CardBody className="text-xs text-slate-400">Real-time attention weights across applications</CardBody>
      </Card>
    </div>
  );
}
