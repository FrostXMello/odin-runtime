"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ProjectsPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "projects"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/projects"),
    refetchInterval: 10000,
  });
  const p = (data?.projects as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Projects</h2>
      <Card>
        <CardHeader title="Registry" subtitle={`${String(p.projects ?? 0)} projects`} />
        <CardBody className="text-xs text-slate-400">Persistent project operating memory</CardBody>
      </Card>
    </div>
  );
}
