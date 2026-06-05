"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardHeader } from "@/components/ui/card";

export default function FocusPage() {
  const start = useMutation({ mutationFn: () => apiFetch("/runtime/focus/start", { method: "POST" }) });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Focus</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => start.mutate()}>Start focus session</button>
      <Card><CardHeader title="Focus mode" subtitle="Interruption filtering active" /></Card>
    </div>
  );
}
