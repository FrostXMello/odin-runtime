"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({ queryKey: ["session-prediction"], queryFn: () => apiFetch<Record<string, unknown>>("/runtime/session-prediction/next", { method: "POST" }), refetchInterval: 12000 });
  return (
    <div className="space-y-4"><h2 className="text-sm font-medium text-slate-200">Session Prediction</h2>
    <Card><CardHeader title="Next task" subtitle="predicted" /><CardBody><pre className="text-[10px] text-slate-500">{JSON.stringify(data ?? {}, null, 2)}</pre></CardBody></Card></div>
  );
}
