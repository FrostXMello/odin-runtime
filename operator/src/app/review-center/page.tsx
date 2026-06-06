"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "review-center"],
    queryFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/engineering-society/convene", {
        method: "POST",
        body: JSON.stringify({ topic: "patch review", patch: "diff" }),
      }),
    refetchInterval: 12000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Review Center</h2>
      <Card>
        <CardHeader title="Peer review" subtitle="approval required" />
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(data ?? {}, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
