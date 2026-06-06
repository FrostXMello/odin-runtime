"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function UpdatesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "updates"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/updates"),
    refetchInterval: 30000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Updates</h2>
      <Card>
        <CardHeader title="Runtime version" subtitle={String(data?.version ?? "—")} />
        <CardBody className="text-xs text-slate-400">Deployment profile and migration status</CardBody>
      </Card>
    </div>
  );
}
