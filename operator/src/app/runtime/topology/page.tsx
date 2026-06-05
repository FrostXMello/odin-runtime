"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { runtimeApi } from "@/lib/api/runtime";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RuntimeTopologyPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "topology"],
    queryFn: () => runtimeApi.topology(),
    refetchInterval: 3000,
  });

  const nodes = (data?.nodes as Array<Record<string, unknown>>) ?? [];
  const edges = (data?.edges as Array<Record<string, unknown>>) ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-medium text-slate-200">Runtime topology</h2>
        <Badge variant="default">transport: {String(data?.transport ?? "—")}</Badge>
        <Badge variant="healthy">{String(data?.worker_count ?? 0)} workers</Badge>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Nodes" subtitle="workers · pools · queues" />
          <CardBody className="space-y-2">
            {nodes.map((n) => (
              <motion.div
                key={String(n.node_id)}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center justify-between rounded border border-odin-border/60 px-3 py-2 font-mono text-xs"
              >
                <span className="text-odin-cyan">{String(n.label)}</span>
                <Badge variant={n.status === "healthy" ? "healthy" : "degraded"}>
                  {String(n.kind)} · {String(n.status)}
                </Badge>
              </motion.div>
            ))}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Flow edges" subtitle="queue → worker → pool" />
          <CardBody className="font-mono text-xs text-slate-400">
            {edges.map((e, i) => (
              <div key={i}>
                {String(e.source)} → {String(e.target)} ({String(e.kind)})
              </div>
            ))}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
