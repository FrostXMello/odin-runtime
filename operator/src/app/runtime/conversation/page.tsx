"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ConversationPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "conversation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/conversation"),
    refetchInterval: 8000,
  });
  const conv = (data?.conversation as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Conversational Runtime</h2>
      <Card>
        <CardHeader title="Mode" subtitle={String(conv.mode ?? "assistant")} />
        <CardBody>
          <p className="text-xs text-slate-400">Turns: {String(conv.turns ?? 0)}</p>
        </CardBody>
      </Card>
    </div>
  );
}
