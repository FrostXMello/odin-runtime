"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function LiveCognitionPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "live-cognition"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/live-cognition"),
    refetchInterval: 5000,
  });
  const cont = (data?.continuous as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Cognition</h2>
      <Card>
        <CardHeader title="Continuous loop" subtitle={`${String(cont.ticks ?? 0)} ticks · ${String(cont.deferred ?? 0)} deferred`} />
        <CardBody className="text-xs text-slate-400">Bounded background reasoning with adaptive throttling</CardBody>
      </Card>
    </div>
  );
}
