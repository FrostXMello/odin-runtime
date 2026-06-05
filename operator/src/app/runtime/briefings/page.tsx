"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function BriefingsPage() {
  const { data } = useQuery({ queryKey: ["runtime", "briefings"], queryFn: () => apiFetch("/runtime/briefings") });
  const b = (data?.briefing as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Briefings</h2>
      <Card>
        <CardHeader title="Daily briefing" subtitle={String(b.summary ?? "No briefing yet")} />
        <CardBody className="text-xs text-slate-400">Local-only notifications</CardBody>
      </Card>
    </div>
  );
}
