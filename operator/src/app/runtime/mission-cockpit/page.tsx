"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function MissionCockpitPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "mission-cockpit"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/agent-execution"),
    refetchInterval: 5000,
  });
  const ae = (data?.agent_execution as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Mission cockpit</h2>
      <Card>
        <CardHeader title="Agent tasks" subtitle={`Queue: ${String(ae.scheduler_queue ?? 0)}`} />
        <CardBody className="font-mono text-xs text-slate-400">Unified mission + agent execution view</CardBody>
      </Card>
    </div>
  );
}
