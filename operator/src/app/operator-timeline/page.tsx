"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "operator-timeline"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognitive-kernel/restore", { method: "POST" }),
    refetchInterval: 15000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Operator Timeline</h2>
      <Card>
        <CardHeader title="Continuity" subtitle="cross-session" />
        <CardBody><pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">{JSON.stringify(data ?? {}, null, 2)}</pre></CardBody>
      </Card>
    </div>
  );
}
