"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeSupervisionPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "supervision"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/supervision"),
    refetchInterval: 3000,
  });
  const reviews = (data?.pending_reviews as unknown[]) ?? [];

  const emergency = useMutation({
    mutationFn: () => apiFetch("/runtime/emergency-stop", { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["runtime", "supervision"] });
      qc.invalidateQueries({ queryKey: ["runtime", "actions"] });
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Supervision</h2>
      <button
        className="rounded bg-red-900/40 px-3 py-1 text-xs text-red-300"
        onClick={() => emergency.mutate()}
      >
        Emergency stop
      </button>
      <Card>
        <CardHeader title="Approval mode" subtitle={`Mode: ${String(data?.mode ?? "—")}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Pending reviews: {reviews.length}
        </CardBody>
      </Card>
    </div>
  );
}
