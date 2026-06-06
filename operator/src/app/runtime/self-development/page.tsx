"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function SelfDevelopmentPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "self-development"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/self-development"),
    refetchInterval: 12000,
  });
  const sd = (data?.self_development as Record<string, unknown>) ?? {};
  const queue = (sd.queue as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Self-Development Supervision</h2>
      <Card>
        <CardHeader title="Improvement queue" subtitle={`${queue.length} proposals`} />
        <CardBody>
          <p className="text-xs text-amber-300/90">All changes require operator approval. No direct self-modification.</p>
        </CardBody>
      </Card>
    </div>
  );
}
