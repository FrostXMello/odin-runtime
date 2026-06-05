"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function DeveloperPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "repositories"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/repositories"),
    refetchInterval: 10000,
  });
  const i = (data?.integrations as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Developer integrations</h2>
      <Card>
        <CardHeader title="Activity" subtitle="VSCode · Cursor · Git (read-only)" />
        <CardBody className="text-xs text-slate-400">Terminal sessions: {String(i.terminal_sessions ?? 0)}</CardBody>
      </Card>
    </div>
  );
}
