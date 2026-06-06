"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function ThoughtStreamPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "thought-stream"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/thought-stream"),
    refetchInterval: 4000,
  });
  const stream = (data?.stream as Record<string, unknown>) ?? {};
  const items = (stream.thought_stream as unknown[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Thought Stream</h2>
      <Card>
        <CardHeader title="Active thoughts" subtitle={`${items.length} items`} />
        <CardBody>
          <ul className="space-y-1 text-xs text-slate-300">
            {items.slice(-8).map((t, i) => (
              <li key={i}>{String((t as Record<string, unknown>).text ?? "")}</li>
            ))}
          </ul>
        </CardBody>
      </Card>
    </div>
  );
}
