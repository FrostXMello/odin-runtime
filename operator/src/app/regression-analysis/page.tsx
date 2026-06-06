"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "regression-analysis"],
    queryFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/autonomous-debugging/analyze", {
        method: "POST",
        body: JSON.stringify({ stacktrace: "Error: regression in federation\\n  at test_retry" }),
      }),
    refetchInterval: 11000,
  });
  const risk = (data?.risk as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Regression Analysis</h2>
      <Card>
        <CardHeader title="Risk scoring" subtitle="supervised hypotheses" />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify({ risk, hypothesis: data?.hypothesis }, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
