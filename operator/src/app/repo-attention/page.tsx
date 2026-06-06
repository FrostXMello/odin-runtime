"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "repo-attention"],
    queryFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/live-engineering/observe", {
        method: "POST",
        body: JSON.stringify({ repo: "odin-runtime", file: "app.py" }),
      }),
    refetchInterval: 9000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Repo Attention</h2>
      <Card>
        <CardHeader title="Drift & focus" subtitle="engineering context" />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify({ drift: data?.drift, context: data?.context }, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
