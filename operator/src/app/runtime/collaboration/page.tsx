"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeCollaborationPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "collaboration"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/collaboration"),
    refetchInterval: 5000,
  });
  const pending = (data?.pending_approvals as unknown[]) ?? [];
  const history = (data?.approval_history as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Human collaboration</h2>
      <Card>
        <CardHeader title="Approval queue" subtitle={`Pending: ${pending.length}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          {pending.length === 0 ? (
            <div>No pending approvals</div>
          ) : (
            pending.map((a, i) => {
              const item = a as Record<string, unknown>;
              return <div key={i}>{String(item.action)} — {String(item.detail).slice(0, 80)}</div>;
            })
          )}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Recent decisions" subtitle={`${history.length} resolved`} />
        <CardBody className="font-mono text-xs text-slate-400">
          {history.length === 0 ? "—" : `${history.length} approval(s) in history`}
        </CardBody>
      </Card>
    </div>
  );
}
