"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "debug-watchtower"],
    queryFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/live-engineering/observe", {
        method: "POST",
        body: JSON.stringify({ repo: "odin", error: "sample trace" }),
      }),
    refetchInterval: 10000,
  });
  const tower = (data?.watchtower as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Debug Watchtower</h2>
      <Card>
        <CardHeader title="Active issues" subtitle="supervised debugging" />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(tower, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
