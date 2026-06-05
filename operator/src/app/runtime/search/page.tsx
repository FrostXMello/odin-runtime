"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const search = useMutation({
    mutationFn: (query: string) =>
      apiFetch("/runtime/search", { method: "POST", body: JSON.stringify({ query, limit: 10 }) }),
  });
  const results = (search.data as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Local search</h2>
      <input className="w-full rounded border border-odin-border bg-odin-panel px-2 py-1 text-xs" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search projects, files, memory..." />
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => search.mutate(q)}>Search</button>
      <Card>
        <CardHeader title="Results" subtitle={`${String(results.count ?? 0)} hits`} />
        <CardBody className="font-mono text-xs text-slate-400">{JSON.stringify(results.results ?? [], null, 2).slice(0, 500)}</CardBody>
      </Card>
    </div>
  );
}
