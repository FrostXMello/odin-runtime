"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeActionsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "actions"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/actions"),
    refetchInterval: 3000,
  });
  const pending = (data?.pending_approval as unknown[]) ?? [];
  const recent = (data?.recent as unknown[]) ?? [];

  const propose = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/actions/propose", {
        method: "POST",
        body: JSON.stringify({ kind: "click", label: "Test click", payload: { x: 100, y: 200 } }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "actions"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Action engine</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => propose.mutate()}
      >
        Propose test action
      </button>
      <Card>
        <CardHeader title="Approval queue" subtitle={`Pending: ${pending.length}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          {pending.length === 0 ? (
            <div>No pending actions</div>
          ) : (
            pending.map((a, i) => {
              const item = a as Record<string, unknown>;
              return (
                <div key={i}>
                  {String(item.label)} — {String(item.state)} ({String(item.risk)})
                </div>
              );
            })
          )}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Recent actions" subtitle={`${recent.length} entries`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Emergency stopped: {String(data?.emergency_stopped ?? false)}
        </CardBody>
      </Card>
    </div>
  );
}
