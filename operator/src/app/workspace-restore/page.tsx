"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "workspace-restore"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/operator-experience/startup", { method: "POST" }),
    refetchInterval: 15000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Workspace Restore</h2>
      <Card>
        <CardHeader title="Rehydration" subtitle={data?.accepted ? "restored" : "pending"} />
        <CardBody>
          <p className="mb-2 text-xs text-slate-400">Resume unfinished work, repo context, and cognitive checkpoints.</p>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(data ?? {}, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
