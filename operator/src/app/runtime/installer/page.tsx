"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

const btn = "rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan";

export default function InstallerPage() {
  const { data, refetch } = useQuery({
    queryKey: ["runtime", "deployment-validate"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/deployment/validate", { method: "POST" }),
    enabled: false,
  });
  const bootstrap = useMutation({
    mutationFn: () => apiFetch<Record<string, unknown>>("/runtime/deployment/bootstrap", { method: "POST", body: {} }),
    onSuccess: () => refetch(),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Installer</h2>
      <Card>
        <CardHeader title="Environment validation" subtitle={data?.valid ? "Valid" : "Run validation"} />
        <CardBody className="flex gap-2">
          <button type="button" className={btn} onClick={() => refetch()}>Validate</button>
          <button type="button" className={btn} onClick={() => bootstrap.mutate()}>Bootstrap</button>
        </CardBody>
      </Card>
    </div>
  );
}
