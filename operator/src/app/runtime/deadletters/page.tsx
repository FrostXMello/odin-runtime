"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

interface DeadLetterResponse {
  count: number;
  items: Array<{
    deadletter_id: string;
    mission_id?: string;
    reason: string;
    replay_count: number;
  }>;
}

export default function RuntimeDeadlettersPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "deadletters"],
    queryFn: () => apiFetch<DeadLetterResponse>("/runtime/deadletters"),
    refetchInterval: 5000,
  });
  const replay = useMutation({
    mutationFn: (id: string) =>
      apiFetch(`/runtime/deadletters/${id}/replay`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "deadletters"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Dead letter queue</h2>
      <Card>
        <CardHeader title="Failed items" subtitle={`${data?.count ?? 0} total`} />
        <CardBody className="space-y-2">
          {(data?.items ?? []).map((item) => (
            <div
              key={item.deadletter_id}
              className="flex items-center justify-between rounded border border-odin-border/50 px-2 py-1.5 text-xs"
            >
              <span className="font-mono text-odin-muted">{item.deadletter_id.slice(0, 10)}…</span>
              <span className="text-amber-300">{item.reason}</span>
              <button
                type="button"
                className="text-odin-cyan hover:underline"
                onClick={() => replay.mutate(item.deadletter_id)}
              >
                Replay
              </button>
            </div>
          ))}
          {!data?.items?.length && <p className="text-xs text-odin-muted">No dead letters.</p>}
        </CardBody>
      </Card>
    </div>
  );
}
