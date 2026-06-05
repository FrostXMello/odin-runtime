"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { useTraceStream } from "@/hooks/useMissionStream";
import { LiveIndicator } from "@/components/stream/live-indicator";
import { useOperatorStore } from "@/store/operator-store";
import { eventColor } from "@/lib/timeline/event-meta";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import type { TraceEventRecord } from "@/lib/api/types";

function SpanTree({ events }: { events: TraceEventRecord[] }) {
  const roots = events.filter((e) => !e.parent_span_id);
  const children = (parent: string) =>
    events.filter((e) => e.parent_span_id === parent);

  function Node({ e, depth }: { e: TraceEventRecord; depth: number }) {
    const kids = children(e.span_id);
    const color = eventColor(e.kind);
    return (
      <div style={{ marginLeft: depth * 16 }} className="border-l border-odin-border/60 pl-3 py-1">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
          <span className="text-[10px] uppercase" style={{ color }}>
            {e.kind}
          </span>
          <span className="text-xs text-slate-400">{e.message}</span>
          {e.duration_ms != null && (
            <span className="font-mono text-[10px] text-odin-muted">{e.duration_ms.toFixed(1)}ms</span>
          )}
        </div>
        {e.mission_id && (
          <Link href={`/missions/${e.mission_id}`} className="text-[10px] text-odin-cyan">
            mission {e.mission_id.slice(0, 8)}…
          </Link>
        )}
        {kids.map((k) => (
          <Node key={k.event_id} e={k} depth={depth + 1} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {roots.length ? roots.map((r) => <Node key={r.event_id} e={r} depth={0} />) : events.map((e) => <Node key={e.event_id} e={e} depth={0} />)}
    </div>
  );
}

export function TraceExplorer({ traceId }: { traceId: string }) {
  const live = useOperatorStore((s) => s.liveRefresh);
  const stream = useTraceStream(traceId, live);
  const streamOn = stream.metrics?.status === "connected";
  const poll = useOperatorStore((s) => s.pollIntervalMs);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["trace", traceId],
    queryFn: () => runtimeApi.trace(traceId),
    refetchInterval: live && !streamOn ? poll * 2 : false,
  });

  if (isLoading) return <p className="text-odin-muted">Loading trace…</p>;
  if (isError || !data?.trace_id) {
    return <p className="text-rose-400">Trace not found</p>;
  }

  const duration =
    data.started_at && data.ended_at
      ? new Date(data.ended_at).getTime() - new Date(data.started_at).getTime()
      : null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <LiveIndicator channel={`trace:${traceId}`} />
      </div>
      <div className="font-mono text-xs text-odin-muted">
        <p>
          <span className="text-slate-400">trace_id</span> {data.trace_id}
        </p>
        <p>
          <span className="text-slate-400">causal_chain</span> {data.causal_chain_id}
        </p>
        <p>
          <span className="text-slate-400">events</span> {data.event_count}
          {duration != null && ` · ${duration}ms span`}
        </p>
      </div>

      <Card>
        <CardHeader title="Causal hierarchy" />
        <CardBody>
          <SpanTree events={data.events} />
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Event log" subtitle="Chronological" />
        <CardBody className="max-h-96 overflow-auto">
          <table className="w-full text-left text-[10px]">
            <thead>
              <tr className="text-odin-muted">
                <th className="py-1">Time</th>
                <th>Kind</th>
                <th>Component</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {data.events.map((e) => (
                <tr key={e.event_id} className="border-t border-odin-border/30">
                  <td className="py-1 font-mono text-odin-muted">
                    {new Date(e.timestamp).toLocaleTimeString()}
                  </td>
                  <td style={{ color: eventColor(e.kind) }}>{e.kind}</td>
                  <td>{e.component}</td>
                  <td className="text-slate-400">{e.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
