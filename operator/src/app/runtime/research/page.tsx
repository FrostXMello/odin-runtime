"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeResearchPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "research"],
    queryFn: () => apiFetch<{ sessions: Array<Record<string, unknown>> }>("/runtime/research/debate"),
    refetchInterval: 10000,
  });
  const sessions = data?.sessions ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Research sessions</h2>
      <Card>
        <CardHeader title="Active research" subtitle={`${sessions.length} sessions`} />
        <CardBody className="space-y-1 font-mono text-xs text-slate-400">
          {sessions.map((s) => (
            <div key={String(s.session_id)}>
              {String(s.topic)?.slice(0, 60)} · {String(s.status)} · iter{" "}
              {String((s.iterations as unknown[])?.length ?? 0)}
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
