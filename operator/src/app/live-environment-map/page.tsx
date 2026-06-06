"use client";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
export default function Page() {
  const { data } = useQuery({
    queryKey: ["runtime", "live-environment-map"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/environment-intelligence/observe", { method: "POST", body: JSON.stringify({ repo: "odin", file: "app.py", title: "Odin Runtime", app_name: "cursor" }) }),
    refetchInterval: 10000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Environment Map</h2>
      <Card>
        <CardHeader title="Workspace semantics" subtitle="intent inference" />
        <CardBody><pre className="max-h-72 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">{JSON.stringify(data ?? {}, null, 2)}</pre></CardBody>
      </Card>
    </div>
  );
}
