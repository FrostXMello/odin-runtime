"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function PatchesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "patches"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/patches"),
    refetchInterval: 10000,
  });
  const p = (data?.patching as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Supervised Patches</h2>
      <Card>
        <CardHeader title="Patch sandbox" subtitle={`${String(p.patches ?? 0)} sandboxed · approval required`} />
        <CardBody className="text-xs text-slate-400">No direct main commits. Rollback plans mandatory.</CardBody>
      </Card>
    </div>
  );
}
