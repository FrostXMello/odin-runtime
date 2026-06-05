"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeFederationPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "federation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/federation"),
    refetchInterval: 8000,
  });
  const snap = (data?.snapshot as Record<string, unknown>) ?? {};

  const connect = useMutation({
    mutationFn: () =>
      apiFetch("/runtime/federation/connect", {
        method: "POST",
        body: JSON.stringify({ name: "peer-node", mode: "trusted_cluster" }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "federation"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Federation</h2>
      <button
        className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
        onClick={() => connect.mutate()}
      >
        Connect peer
      </button>
      <Card>
        <CardHeader title="Topology" subtitle={`Mode: ${String(snap.mode ?? "isolated")}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Local node: {String(snap.local_node_id ?? "—")}</div>
          <div>Edges: {String((snap.topology as Record<string, unknown>)?.edge_count ?? 0)}</div>
        </CardBody>
      </Card>
    </div>
  );
}
