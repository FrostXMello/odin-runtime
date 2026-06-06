"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function UpgradeCyclesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "upgrade-cycles"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/upgrade-cycles"),
    refetchInterval: 8000,
  });
  const evo = (data?.evolution as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Upgrade Cycles</h2>
      <Card>
        <CardHeader title="Depth guard" subtitle={String(evo.depth ?? 0)} />
        <CardBody>
          <p className="text-xs text-slate-400">Cooldown: {String(evo.cooldown_s ?? 60)}s · Recursion bounded</p>
        </CardBody>
      </Card>
    </div>
  );
}
