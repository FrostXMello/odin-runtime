"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "persistent-cognition"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/persistent-cognition"),
    refetchInterval: 9000,
  });
  const root = (data?.["persistent_cognition"] as Record<string, unknown>) ?? data ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Persistent Cognition</h2>
      <Card>
        <CardHeader title="Status" subtitle="active" />
        <CardBody><p className="text-xs text-slate-400">Persistent cognitive operating layer — local-first continuity.</p></CardBody>
      </Card>
    </div>
  );
}
