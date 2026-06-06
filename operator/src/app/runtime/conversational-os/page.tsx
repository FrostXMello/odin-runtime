"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ConversationalOSPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "conversational-os"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/conversational-os"),
    refetchInterval: 8000,
  });
  const os = (data?.conversational_os as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Conversational OS</h2>
      <Card>
        <CardHeader title="Turns" subtitle={String(os.turns ?? 0)} />
        <CardBody><p className="text-xs text-slate-400">Natural command routing with persistent threads.</p></CardBody>
      </Card>
    </div>
  );
}
