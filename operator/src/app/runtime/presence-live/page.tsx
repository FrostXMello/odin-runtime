"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function PresenceLivePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "presence-live"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/presence-live"),
    refetchInterval: 9000,
  });
  const style = (data?.style as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Presence</h2>
      <Card>
        <CardHeader title="Familiarity" subtitle={String(style.familiarity ?? "0.6")} />
        <CardBody><p className="text-xs text-amber-300/90">Simulated continuity — not consciousness.</p></CardBody>
      </Card>
    </div>
  );
}
