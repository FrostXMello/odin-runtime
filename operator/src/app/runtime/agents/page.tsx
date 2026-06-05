"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeAgentsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "agents"],
    queryFn: () => apiFetch<{ agents: string[] }>("/runtime/agents"),
    refetchInterval: 10000,
  });
  const agents = data?.agents ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Cognitive agents</h2>
      <Card>
        <CardHeader title="Active agents" subtitle={`${agents.length} registered`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {agents.map((a) => (
            <div key={a}>{a}</div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
