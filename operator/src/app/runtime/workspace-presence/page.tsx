"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "workspace-presence"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/workspace-presence"),
    refetchInterval: 9000,
  });
  const root = (data?.["workspace_presence"] as Record<string, unknown>) ?? data ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Workspace Presence</h2>
      <Card>
        <CardHeader title="Status" subtitle="active" />
        <CardBody><p className="text-xs text-slate-400">Persistent cognitive operating layer — local-first continuity.</p></CardBody>
      </Card>
    </div>
  );
}
