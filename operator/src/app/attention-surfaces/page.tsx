"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "attention-surfaces"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognitive-streams/push", { method: "POST", body: JSON.stringify({ thought: "attention surface active" }) }),
    refetchInterval: 9000,
  });
  const attn = (data?.attention as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Attention Surfaces</h2>
      <Card>
        <CardHeader title="Live attention" subtitle="stream routing" />
        <CardBody><pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">{JSON.stringify(attn, null, 2)}</pre></CardBody>
      </Card>
    </div>
  );
}
