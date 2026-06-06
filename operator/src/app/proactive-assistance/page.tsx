"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "proactive-assistance"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/proactive-assistance/evaluate", { method: "POST", body: JSON.stringify({ context: "engineering", idle_s: 60 }) }),
    refetchInterval: 12000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Proactive Assistance</h2>
      <Card>
        <CardHeader title="Non-invasive hints" subtitle="operator-controlled" />
        <CardBody><pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">{JSON.stringify(data ?? {}, null, 2)}</pre></CardBody>
      </Card>
    </div>
  );
}
