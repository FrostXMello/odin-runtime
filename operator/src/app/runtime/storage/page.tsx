"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardHeader } from "@/components/ui/card";

export default function StoragePage() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["runtime", "storage"], queryFn: () => apiFetch("/runtime/storage") });
  const s = (data?.storage as Record<string, unknown>) ?? {};
  const opt = useMutation({
    mutationFn: () => apiFetch("/runtime/storage/optimize", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "storage"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Storage</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => opt.mutate()}>Optimize storage</button>
      <Card><CardHeader title="Cache" subtitle={`${String(s.cache_size ?? 0)} entries · cold ${String(s.cold_storage ?? 0)}`} /></Card>
    </div>
  );
}
