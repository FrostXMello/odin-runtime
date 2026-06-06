"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({ queryKey: ["upgrade-planning"], queryFn: () => apiFetch<Record<string, unknown>>("/runtime/upgrade-planning/propose", { method: "POST", body: JSON.stringify({ goal: "modularize federation layer" }) }), refetchInterval: 15000 });
  return (
    <div className="space-y-4"><h2 className="text-sm font-medium text-slate-200">Upgrade Planning</h2>
    <Card><CardHeader title="Proposals" subtitle="approval required" /><CardBody><pre className="text-[10px] text-slate-500">{JSON.stringify(data?.proposal ?? data ?? {}, null, 2)}</pre></CardBody></Card></div>
  );
}
