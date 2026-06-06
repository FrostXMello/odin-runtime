"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RetrievalPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "retrieval"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/retrieval"),
    refetchInterval: 10000,
  });
  const vm = (data?.vector_memory as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Retrieval</h2>
      <Card>
        <CardHeader title="Memory stores" subtitle={`episodes ${String(vm.episodes ?? 0)} · long-term ${String(vm.long_term ?? 0)}`} />
        <CardBody className="text-xs text-slate-400">Hybrid retrieval with temporal relevance and project stitching</CardBody>
      </Card>
    </div>
  );
}
