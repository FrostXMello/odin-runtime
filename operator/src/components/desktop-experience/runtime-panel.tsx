"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

type Props = {
  title: string;
  subtitle: string;
  endpoint: string;
  rootKey?: string;
  description: string;
};

export function DesktopExperiencePanel({ title, subtitle, endpoint, rootKey, description }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ["runtime", endpoint],
    queryFn: () => apiFetch<Record<string, unknown>>(endpoint),
    refetchInterval: 8000,
  });
  const root = rootKey ? ((data?.[rootKey] as Record<string, unknown>) ?? {}) : (data ?? {});
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">{title}</h2>
      <Card>
        <CardHeader title={subtitle} subtitle={isLoading ? "loading…" : "live"} />
        <CardBody className="space-y-2">
          <p className="text-xs text-slate-400">{description}</p>
          <pre className="max-h-64 overflow-auto rounded bg-black/30 p-2 font-mono text-[10px] text-slate-500">
            {JSON.stringify(root, null, 2)}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}
