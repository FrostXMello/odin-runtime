"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "evolution-review-v46"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/evolution-review/open", { method: "POST" }),
    refetchInterval: 12000,
  });
  const review = (data?.review as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Evolution Review</h2>
      <Card>
        <CardHeader title="Supervised upgrades" subtitle={data?.approval_required ? "approval required" : "review"} />
        <CardBody>
          <p className="mb-2 text-xs text-slate-400">Visual patch proposals — no automatic main-branch modification.</p>
          <pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(review, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
