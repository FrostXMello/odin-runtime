"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeDialoguesPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "dialogues"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/society/dialogues"),
    refetchInterval: 5000,
  });
  const dialogues = (data?.dialogues as unknown[]) ?? [];

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Agent dialogues</h2>
      <Card>
        <CardHeader title="Communication stream" subtitle={`${dialogues.length} messages`} />
        <CardBody className="font-mono text-xs text-slate-400">
          Active debates: {((data?.active_debates as unknown[]) ?? []).length}
        </CardBody>
      </Card>
    </div>
  );
}
