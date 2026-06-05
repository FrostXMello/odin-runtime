"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { runtimeApi } from "@/lib/api/runtime";
import { useOperatorStore } from "@/store/operator-store";
import { useMissionStream } from "@/hooks/useMissionStream";
import { LiveIndicator } from "@/components/stream/live-indicator";
import { MissionTimelineView } from "@/components/timeline/mission-timeline";
import { MissionExecutionPanel } from "@/components/missions/mission-execution-panel";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function MissionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const live = useOperatorStore((s) => s.liveRefresh);
  const interval = useOperatorStore((s) => s.pollIntervalMs);
  const stream = useMissionStream(id, live);
  const streamOn = stream.metrics?.status === "connected";

  const { data, isLoading, isError } = useQuery({
    queryKey: ["mission-timeline", id],
    queryFn: () => runtimeApi.missionTimeline(id),
    refetchInterval: live && !streamOn ? interval : live ? interval * 4 : false,
  });

  if (isLoading) return <p className="text-odin-muted">Loading mission timeline…</p>;
  if (isError || !data) return <p className="text-rose-400">Mission not found</p>;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <Badge>{data.current_state}</Badge>
        <LiveIndicator channel={`mission:${id}`} />
        {data.trace_id && (
          <Link href={`/traces/${data.trace_id}`} className="font-mono text-xs text-odin-cyan hover:underline">
            trace {data.trace_id.slice(0, 16)}…
          </Link>
        )}
        <span className="text-xs text-odin-muted">{data.entry_count} events</span>
        <Link href={`/missions/${id}/waterfall`} className="text-xs text-odin-cyan hover:underline">
          waterfall
        </Link>
      </div>
      <MissionExecutionPanel missionId={id} />
      <Card>
        <CardHeader title="Execution timeline" subtitle={`Mission ${id}`} />
        <CardBody>
          <MissionTimelineView
            entries={data.entries}
            traceId={data.trace_id}
            causalChainId={data.causal_chain_id}
          />
        </CardBody>
      </Card>
    </div>
  );
}
