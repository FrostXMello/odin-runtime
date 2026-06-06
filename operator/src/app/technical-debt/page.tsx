"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({ queryKey: ["technical-debt"], queryFn: () => apiFetch<Record<string, unknown>>("/runtime/engineering-evolution/analyze", { method: "POST", body: JSON.stringify({ repo: "odin" }) }), refetchInterval: 15000 });
  return (
    <div className="space-y-4"><h2 className="text-sm font-medium text-slate-200">Technical Debt</h2>
    <Card><CardHeader title="Debt analysis" subtitle="predictive" /><CardBody><pre className="text-[10px] text-slate-500">{JSON.stringify(data?.debt ?? data ?? {}, null, 2)}</pre></CardBody></Card></div>
  );
}
