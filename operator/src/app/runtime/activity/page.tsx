"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ActivityPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "activity"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/activity"),
    refetchInterval: 10000,
  });
  const startup = (data?.startup as Record<string, unknown>) ?? {};
  const suggestions = (startup.suggestions as string[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Activity Center</h2>
      <Card>
        <CardHeader title="Startup suggestions" subtitle={`${suggestions.length} items`} />
        <CardBody className="space-y-1 text-xs text-slate-400">
          {suggestions.length === 0 ? <p>No suggestions yet.</p> : suggestions.map((s) => <p key={s}>{s}</p>)}
        </CardBody>
      </Card>
    </div>
  );
}
