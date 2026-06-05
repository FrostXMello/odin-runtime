"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeFailuresPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "failures-intel"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/failures/intelligence"),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Failure intelligence</h2>
      {data?.oscillation_detected ? (
        <p className="text-xs text-rose-400">Mission oscillation detected</p>
      ) : null}
      <Card>
        <CardHeader title="Root causes" />
        <CardBody className="text-xs text-slate-400">
          {((data?.root_causes as string[]) ?? []).map((c) => (
            <div key={c}>{c}</div>
          ))}
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Degraded capabilities" />
        <CardBody className="text-xs text-slate-400">
          {((data?.degraded_capabilities as string[]) ?? []).join(", ") || "none"}
        </CardBody>
      </Card>
    </div>
  );
}
