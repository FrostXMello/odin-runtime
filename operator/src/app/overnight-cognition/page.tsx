"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({ queryKey: ["overnight-cognition"], queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognitive-orchestration/daemon-v2/overnight", { method: "POST" }), refetchInterval: 20000 });
  return (
    <div className="space-y-4"><h2 className="text-sm font-medium text-slate-200">Overnight Cognition</h2>
    <Card><CardHeader title="Daemon V2" subtitle="low-power" /><CardBody><pre className="text-[10px] text-slate-500">{JSON.stringify(data ?? {}, null, 2)}</pre></CardBody></Card></div>
  );
}
