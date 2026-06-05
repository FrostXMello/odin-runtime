"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RuntimeToolsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "tools-intel"],
    queryFn: () =>
      apiFetch<{
        tools: Array<{ name: string; capability: string; confidence: number }>;
        capabilities: string[];
        recent_selections: Array<Record<string, unknown>>;
      }>("/runtime/tools"),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Tool intelligence</h2>
      <Card>
        <CardHeader title="Registered tools" />
        <CardBody className="flex flex-wrap gap-1">
          {(data?.tools ?? []).map((t) => (
            <Badge key={t.name} variant="default">
              {t.name} · {t.capability}
            </Badge>
          ))}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Recent selections" />
        <CardBody className="font-mono text-xs text-slate-400">
          {(data?.recent_selections ?? []).slice(-15).reverse().map((d, i) => (
            <div key={i}>
              {String(d.capability)} → {String(d.tool ?? "direct")} ({String(d.confidence)})
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
