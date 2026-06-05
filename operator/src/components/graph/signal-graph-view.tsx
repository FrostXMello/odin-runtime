"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { runtimeApi } from "@/lib/api/runtime";
import { graphToFlow, layoutGraph } from "@/lib/graph/transform";
import { useOperatorStore } from "@/store/operator-store";
import { useStreamStore } from "@/store/stream-store";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export function SignalGraphView() {
  const live = useOperatorStore((s) => s.liveRefresh);
  const interval = useOperatorStore((s) => s.pollIntervalMs);
  const [selected, setSelected] = useState<Node | null>(null);
  const ticker = useStreamStore((s) => s.ticker);
  const { data, isLoading, isError } = useQuery({
    queryKey: ["signal-graph"],
    queryFn: () => runtimeApi.signalGraph(500),
    refetchInterval: live ? interval * 2 : false,
  });

  const initial = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    const { nodes, edges } = graphToFlow(data);
    return { nodes: layoutGraph(nodes, edges), edges };
  }, [data]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);

  useEffect(() => {
    setNodes(initial.nodes);
    setEdges(initial.edges);
  }, [initial, setNodes, setEdges]);

  useEffect(() => {
    const latest = ticker.find(
      (e) => e.event_type === "signal_propagated" || e.event_type === "signal_suppressed"
    );
    if (!latest) return;
    const ids = new Set<string>();
    const mid = latest.mission_id;
    const tid = latest.task_id;
    for (const n of nodes) {
      const d = n.data as Record<string, unknown>;
      if (
        (mid && (d.mission_id === mid || String(n.id).includes(mid))) ||
        (tid && (d.task_id === tid || String(n.id).includes(tid))) ||
        String(d.label ?? "").includes(latest.component)
      ) {
        ids.add(n.id);
      }
    }
    if (!ids.size && nodes[0]) ids.add(nodes[0].id);
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        className: ids.has(n.id) ? "odin-node-flash" : undefined,
      }))
    );
    const t = setTimeout(() => {
      setNodes((nds) => nds.map((n) => ({ ...n, className: undefined })));
    }, 1200);
    return () => clearTimeout(t);
  }, [ticker, nodes, setNodes]);

  const onNodeClick = useCallback((_: unknown, node: Node) => {
    setSelected(node);
  }, []);

  if (isLoading) return <p className="text-sm text-odin-muted">Loading signal graph…</p>;
  if (isError) return <p className="text-sm text-rose-400">Failed to load graph</p>;

  return (
    <div className="grid h-[calc(100vh-8rem)] gap-4 lg:grid-cols-[1fr_280px]">
      <Card className="overflow-hidden">
        <CardHeader
          title="Signal lineage"
          subtitle={`${data?.node_count ?? 0} nodes · ${data?.edge_count ?? 0} edges`}
        />
        <CardBody className="h-[calc(100%-3rem)] p-0">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            className="bg-odin-bg"
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#1a2236" gap={20} />
            <Controls className="!bg-odin-panel !border-odin-border" />
            <MiniMap
              nodeColor="#3b82f6"
              maskColor="rgba(7,9,15,0.8)"
              className="!bg-odin-panel"
            />
          </ReactFlow>
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Node inspector" />
        <CardBody className="font-mono text-[10px] text-slate-400">
          {selected ? (
            <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap">
              {JSON.stringify(selected.data, null, 2)}
            </pre>
          ) : (
            <p className="text-odin-muted">Hover or click a node</p>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
