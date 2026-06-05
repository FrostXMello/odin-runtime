"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeBrowserPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "browser"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/browser"),
    refetchInterval: 5000,
  });

  const start = useMutation({
    mutationFn: () => apiFetch("/runtime/browser/session/start", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "browser"] }),
  });

  const session = (data?.active_session as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Browser operator</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => start.mutate()}
      >
        Start session
      </button>
      <Card>
        <CardHeader title="Session monitor" subtitle={`Enabled: ${String(data?.enabled ?? false)}`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Active: {String(session.id ?? "—")}
        </CardBody>
      </Card>
    </div>
  );
}
