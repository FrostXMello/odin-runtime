"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RecoveryPage() {
  const qc = useQueryClient();
  const recover = useMutation({
    mutationFn: () => apiFetch("/runtime/stability/recover", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "stability"] }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Recovery</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => recover.mutate()}>Recover runtime</button>
      <Card>
        <CardHeader title="Crash recovery" subtitle="Restore sessions and tasks" />
        <CardBody className="text-xs text-slate-400">Triggers runtime_recovered trace events.</CardBody>
      </Card>
    </div>
  );
}
