import type { Edge, Node } from "@xyflow/react";
import type { SignalGraphExport } from "@/lib/api/types";

const KIND_COLORS: Record<string, string> = {
  signal: "#22d3ee",
  mission: "#8b5cf6",
  destination: "#3b82f6",
  task: "#10b981",
  default: "#64748b",
};

const RELATION_STROKE: Record<string, string> = {
  propagates_to: "#3b82f6",
  suppressed: "#f43f5e",
  replay_block: "#f59e0b",
  policy_block: "#f59e0b",
  triggers: "#8b5cf6",
};

export function graphToFlow(data: SignalGraphExport): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = data.nodes.map((n, i) => {
    const col = KIND_COLORS[n.kind] ?? KIND_COLORS.default;
    return {
      id: n.id,
      position: { x: (i % 8) * 180, y: Math.floor(i / 8) * 100 },
      data: {
        label: n.label,
        kind: n.kind,
        timestamp: n.timestamp,
        metadata: n.metadata,
      },
      style: {
        background: "#0d111c",
        border: `1px solid ${col}`,
        color: "#e2e8f0",
        fontSize: 11,
        borderRadius: 8,
        padding: 8,
        minWidth: 120,
      },
    };
  });

  const edges: Edge[] = data.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.relation,
    animated: e.relation === "propagates_to",
    style: {
      stroke: RELATION_STROKE[e.relation] ?? "#475569",
      strokeWidth: e.relation === "suppressed" ? 2 : 1,
    },
    labelStyle: { fill: "#94a3b8", fontSize: 9 },
  }));

  return { nodes, edges };
}

export function layoutGraph(nodes: Node[], edges: Edge[]): Node[] {
  const adj = new Map<string, string[]>();
  for (const e of edges) {
    if (!adj.has(e.source)) adj.set(e.source, []);
    adj.get(e.source)!.push(e.target);
  }
  const levels = new Map<string, number>();
  const roots = nodes.filter((n) => !edges.some((e) => e.target === n.id));
  const queue = roots.map((n) => ({ id: n.id, level: 0 }));
  const seen = new Set<string>();
  while (queue.length) {
    const { id, level } = queue.shift()!;
    if (seen.has(id)) continue;
    seen.add(id);
    levels.set(id, level);
    for (const t of adj.get(id) ?? []) {
      queue.push({ id: t, level: level + 1 });
    }
  }
  const byLevel = new Map<number, string[]>();
  for (const [id, lvl] of levels) {
    if (!byLevel.has(lvl)) byLevel.set(lvl, []);
    byLevel.get(lvl)!.push(id);
  }
  return nodes.map((n) => {
    const lvl = levels.get(n.id) ?? 0;
    const idx = (byLevel.get(lvl) ?? []).indexOf(n.id);
    const count = (byLevel.get(lvl) ?? []).length;
    return {
      ...n,
      position: {
        x: lvl * 220,
        y: idx * 90 - (count * 45) / 2,
      },
    };
  });
}
