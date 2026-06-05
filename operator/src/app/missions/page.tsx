"use client";

import Link from "next/link";
import { useMissions } from "@/lib/hooks/use-runtime-health";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function MissionsPage() {
  const { data, isLoading, isError } = useMissions();

  return (
    <Card>
      <CardHeader title="Active missions" subtitle="Live from /api/v1/missions" />
      <CardBody>
        {isLoading && <p className="text-sm text-odin-muted">Loading missions…</p>}
        {isError && <p className="text-sm text-rose-400">Failed to load missions</p>}
        <div className="space-y-2">
          {(data ?? []).map((m) => (
            <Link
              key={m.mission_id}
              href={`/missions/${m.mission_id}`}
              className="flex items-center justify-between rounded-lg border border-odin-border/60 bg-odin-bg/40 px-4 py-3 transition-colors hover:border-odin-cyan/40 hover:bg-odin-panel/60"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm text-slate-200">{m.objective}</p>
                <p className="mt-1 font-mono text-[10px] text-odin-muted">{m.mission_id}</p>
              </div>
              <div className="ml-4 flex shrink-0 flex-col items-end gap-1">
                <Badge variant={m.current_state.includes("fail") ? "critical" : "default"}>
                  {m.current_state}
                </Badge>
                <span className="text-[10px] text-odin-muted">
                  {m.active_tasks.length} active · {m.completed_tasks.length} done
                </span>
              </div>
            </Link>
          ))}
          {!isLoading && !data?.length && (
            <p className="py-8 text-center text-odin-muted">No missions in store</p>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
