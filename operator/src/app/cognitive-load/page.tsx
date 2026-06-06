"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({ queryKey: ["cognitive-load"], queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognition-load/balance", { method: "POST", body: JSON.stringify({ load: 0.55 }) }), refetchInterval: 9000 });
  return (
    <div className="space-y-4"><h2 className="text-sm font-medium text-slate-200">Cognitive Load</h2>
    <Card><CardHeader title="Load balancer" subtitle="adaptive" /><CardBody><pre className="text-[10px] text-slate-500">{JSON.stringify(data ?? {}, null, 2)}</pre></CardBody></Card></div>
  );
}
