"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { runtimeApi } from "@/lib/api/runtime";
import { useOperatorStore } from "@/store/operator-store";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import type { MemoryMutation } from "@/lib/api/types";

export function MemoryAuditTable() {
  const live = useOperatorStore((s) => s.liveRefresh);
  const interval = useOperatorStore((s) => s.pollIntervalMs);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("all");

  const { data, isLoading } = useQuery({
    queryKey: ["memory-mutations"],
    queryFn: () => runtimeApi.memoryMutations(200),
    refetchInterval: live ? interval * 2 : false,
  });

  const filtered = useMemo(() => {
    let list = data ?? [];
    if (category !== "all") list = list.filter((m) => m.category === category);
    if (q) {
      const lower = q.toLowerCase();
      list = list.filter(
        (m) =>
          m.actor.toLowerCase().includes(lower) ||
          m.reason.toLowerCase().includes(lower) ||
          (m.mission_id ?? "").includes(lower) ||
          (m.memory_id ?? "").includes(lower)
      );
    }
    return list;
  }, [data, q, category]);

  const categories = useMemo(() => {
    const set = new Set((data ?? []).map((m) => m.category));
    return ["all", ...Array.from(set)];
  }, [data]);

  return (
    <Card>
      <CardHeader title="Memory mutations" subtitle="Live audit trail from Mimir" />
      <CardBody className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <input
            type="search"
            placeholder="Search actor, reason, mission…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="flex-1 min-w-[200px] rounded-lg border border-odin-border bg-odin-bg px-3 py-2 text-sm text-slate-200 placeholder:text-odin-muted focus:border-odin-cyan/50 focus:outline-none"
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-lg border border-odin-border bg-odin-bg px-3 py-2 text-sm text-slate-300"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        {isLoading ? (
          <p className="text-sm text-odin-muted">Loading…</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-odin-border text-odin-muted">
                  <th className="py-2 pr-4">Time</th>
                  <th className="py-2 pr-4">Actor</th>
                  <th className="py-2 pr-4">Category</th>
                  <th className="py-2 pr-4">Hashes</th>
                  <th className="py-2 pr-4">Mission</th>
                  <th className="py-2">Trace</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((m: MemoryMutation) => (
                  <tr key={m.mutation_id} className="border-b border-odin-border/40 hover:bg-odin-bg/50">
                    <td className="py-2 pr-4 font-mono text-odin-muted">
                      {new Date(m.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2 pr-4">{m.actor}</td>
                    <td className="py-2 pr-4">{m.category}</td>
                    <td className="py-2 pr-4 font-mono text-[10px]">
                      {m.previous_hash?.slice(0, 8) ?? "—"} → {m.new_hash?.slice(0, 8) ?? "—"}
                    </td>
                    <td className="py-2 pr-4">
                      {m.mission_id ? (
                        <Link href={`/missions/${m.mission_id}`} className="text-odin-cyan hover:underline">
                          {m.mission_id.slice(0, 10)}…
                        </Link>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="py-2">
                      {m.trace_id ? (
                        <Link href={`/traces/${m.trace_id}`} className="text-odin-cyan hover:underline">
                          trace
                        </Link>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <p className="py-6 text-center text-odin-muted">No mutations recorded yet</p>
            )}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
