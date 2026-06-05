"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function SessionContinuityPage() {
  const restore = useMutation({
    mutationFn: () => apiFetch("/runtime/copilot/restore-workspace", { method: "POST" }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Session continuity</h2>
      <button className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => restore.mutate()}>Restore workspace</button>
      <Card>
        <CardHeader title="Context restoration" subtitle="Copilot workspace snapshots" />
        <CardBody className="text-xs text-slate-400">Restores latest IDE, terminal, and browser context.</CardBody>
      </Card>
    </div>
  );
}
