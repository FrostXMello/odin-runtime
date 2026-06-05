"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeWorkspacePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "workspace"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/workspace"),
    refetchInterval: 8000,
  });
  const patterns = (data?.patterns as Record<string, unknown>[]) ?? [];
  const workspace = (data?.workspace as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Workspace memory</h2>
      <Card>
        <CardHeader title="Active workspace" subtitle={`Session: ${String(workspace.session_id ?? "—")}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          {patterns.length === 0 ? (
            <div>No learned patterns yet</div>
          ) : (
            patterns.map((p, i) => (
              <div key={i}>
                {String(p.label)} ({String(p.count)}x)
              </div>
            ))
          )}
        </CardBody>
      </Card>
    </div>
  );
}
