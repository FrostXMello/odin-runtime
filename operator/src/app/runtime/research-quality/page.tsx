"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ResearchQualityPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "research-quality"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/research-quality"),
    refetchInterval: 15000,
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Research Quality</h2>
      <Card>
        <CardHeader title="Synthesis validation" subtitle="Source trust and citation quality" />
        <CardBody className="text-xs text-slate-400">Contradiction resolution and long-horizon topic tracking</CardBody>
      </Card>
    </div>
  );
}
