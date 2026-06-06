"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

function Page({ title, endpoint, subtitleKey, subtitle }: { title: string; endpoint: string; subtitleKey: string; subtitle?: string }) {
  const { data } = useQuery({
    queryKey: ["runtime", endpoint.replace("/runtime/", "")],
    queryFn: () => apiFetch<Record<string, unknown>>(endpoint),
    refetchInterval: 8000,
  });
  const root = data ?? {};
  const nested = (root[subtitleKey] as Record<string, unknown>) ?? root;
  const label = subtitle ?? String(nested.mode ?? nested.items ?? nested.turns ?? nested.repo ?? "active");
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">{title}</h2>
      <Card>
        <CardHeader title="Status" subtitle={label} />
        <CardBody><p className="text-xs text-slate-400">Native cognitive desktop layer — local-first, supervised.</p></CardBody>
      </Card>
    </div>
  );
}

export default function NativeShellPage() {
  return <Page title="Native Desktop Shell" endpoint="/runtime/native-shell" subtitleKey="shell" subtitle="online" />;
}
