"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RuntimeWorkersPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "workers-registry"],
    queryFn: () => runtimeApi.workersRegistry(),
    refetchInterval: 3000,
  });

  const drain = useMutation({
    mutationFn: (id: string) => runtimeApi.drainWorker(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "workers-registry"] }),
  });

  const workers = data?.workers ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">
        Workers · local {data?.local_worker_id?.slice(0, 12)}…
      </h2>
      <Card>
        <CardHeader title="Registered workers" subtitle="capability distribution" />
        <CardBody className="space-y-2">
          {workers.map((w) => (
            <div
              key={String(w.worker_id)}
              className="flex flex-wrap items-center justify-between gap-2 rounded border border-odin-border/60 px-3 py-2 text-xs"
            >
              <span className="font-mono text-odin-cyan">{String(w.worker_id)}</span>
              <div className="flex flex-wrap gap-1">
                {(w.capabilities as string[] | undefined)?.map((c) => (
                  <Badge key={c} variant="default">
                    {c}
                  </Badge>
                ))}
              </div>
              <div className="flex items-center gap-2">
                {w.stale ? <Badge variant="critical">stale</Badge> : <Badge variant="healthy">live</Badge>}
                {w.draining ? <Badge variant="degraded">draining</Badge> : null}
                <button
                  type="button"
                  className="rounded bg-odin-border/60 px-2 py-1 text-[10px] hover:bg-odin-accent/20"
                  onClick={() => drain.mutate(String(w.worker_id))}
                >
                  drain
                </button>
              </div>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
