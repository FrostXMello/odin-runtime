"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeDesktopPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "desktop"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/desktop"),
    refetchInterval: 5000,
  });
  const active = (data?.active_window as Record<string, unknown>) ?? {};
  const timeline = (data?.timeline as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Desktop awareness</h2>
      <Card>
        <CardHeader title="Active window" subtitle={`Enabled: ${String(data?.enabled ?? false)}`} />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>App: {String(active.app ?? "—")}</div>
          <div>Title: {String(active.title ?? "—")}</div>
          <div>Timeline segments: {timeline.length}</div>
        </CardBody>
      </Card>
    </div>
  );
}
