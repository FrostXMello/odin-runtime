"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function TracesIndexPage() {
  const { data } = useQuery({
    queryKey: ["causal-events"],
    queryFn: () => runtimeApi.causalEvents(80),
    refetchInterval: 5000,
  });

  const traces = new Map<string, { count: number; last: string; chain: string }>();
  for (const e of data?.causal_events ?? []) {
    const cur = traces.get(e.trace_id);
    if (!cur) {
      traces.set(e.trace_id, { count: 1, last: e.kind, chain: e.causal_chain_id });
    } else {
      cur.count += 1;
      cur.last = e.kind;
    }
  }

  return (
    <Card>
      <CardHeader title="Recent traces" subtitle="From causal event store" />
      <CardBody className="space-y-2">
        {Array.from(traces.entries()).map(([tid, meta]) => (
          <Link
            key={tid}
            href={`/traces/${tid}`}
            className="flex justify-between rounded-lg border border-odin-border/50 px-3 py-2 hover:border-odin-cyan/40"
          >
            <span className="font-mono text-xs text-odin-cyan">{tid}</span>
            <span className="text-[10px] text-odin-muted">
              {meta.count} events · {meta.last}
            </span>
          </Link>
        ))}
        {traces.size === 0 && <p className="text-odin-muted text-sm">No traces yet — run a mission first</p>}
      </CardBody>
    </Card>
  );
}
