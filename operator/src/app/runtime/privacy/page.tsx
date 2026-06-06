"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function PrivacyPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "privacy"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/privacy"),
    refetchInterval: 15000,
  });
  const p = (data?.privacy as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Privacy</h2>
      <Card>
        <CardHeader title="Permission audit" subtitle={`${String(p.audit_entries ?? 0)} entries`} />
        <CardBody className="text-xs text-slate-400">Local-first credential vault and sensitive-data masking</CardBody>
      </Card>
    </div>
  );
}
