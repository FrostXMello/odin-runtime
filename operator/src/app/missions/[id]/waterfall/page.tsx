"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { useMissionStream } from "@/hooks/useMissionStream";
import { LiveIndicator } from "@/components/stream/live-indicator";

interface MissionExecutionsResponse {
  executions: Array<{
    execution_id: string;
    task_id?: string;
    state: string;
    started_at?: string;
    ended_at?: string;
    capability_used: string;
  }>;
}

export default function MissionWaterfallPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  useMissionStream(id, true);

  const { data } = useQuery({
    queryKey: ["mission-executions", id],
    queryFn: () => apiFetch<MissionExecutionsResponse>(`/missions/${id}/executions`),
    refetchInterval: 2000,
  });

  const execs = data?.executions ?? [];
  const t0 = execs.reduce((min, e) => {
    const t = e.started_at ? new Date(e.started_at).getTime() : min;
    return Math.min(min, t);
  }, Date.now());

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-medium text-slate-200">Execution waterfall</h2>
        <LiveIndicator channel={`mission:${id}`} />
      </div>
      <Card>
        <CardHeader title="Parallel lanes" subtitle={`${execs.length} executions`} />
        <CardBody>
          <div className="space-y-3">
            {execs.map((ex) => {
              const start = ex.started_at ? new Date(ex.started_at).getTime() : t0;
              const end = ex.ended_at ? new Date(ex.ended_at).getTime() : Date.now();
              const offset = Math.max(0, ((start - t0) / 1000) * 40);
              const width = Math.max(24, ((end - start) / 1000) * 40);
              return (
                <div key={ex.execution_id} className="relative h-8">
                  <span className="absolute left-0 top-1 w-24 truncate font-mono text-[9px] text-odin-muted">
                    {ex.task_id?.slice(0, 8) ?? ex.execution_id.slice(0, 8)}
                  </span>
                  <div
                    className="absolute top-0 h-6 rounded bg-odin-cyan/30 border border-odin-cyan/50"
                    style={{ left: 100 + offset, width }}
                    title={ex.capability_used}
                  />
                  <span className="absolute right-0 top-1 text-[9px] uppercase text-slate-400">
                    {ex.state}
                  </span>
                </div>
              );
            })}
            {!execs.length && <p className="text-xs text-odin-muted">No executions recorded yet.</p>}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
