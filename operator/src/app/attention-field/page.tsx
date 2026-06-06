"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({ queryKey: ["attention-field"], queryFn: () => apiFetch<Record<string, unknown>>("/runtime/operator-intelligence-v2/analyze", { method: "POST", body: JSON.stringify({ hours: 6, switches: 8 }) }), refetchInterval: 11000 });
  return (
    <div className="space-y-4"><h2 className="text-sm font-medium text-slate-200">Attention Field</h2>
    <Card><CardHeader title="Heatmap" subtitle="live" /><CardBody><pre className="text-[10px] text-slate-500">{JSON.stringify(data?.assistance ?? data ?? {}, null, 2)}</pre></CardBody></Card></div>
  );
}
