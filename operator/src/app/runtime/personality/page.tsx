"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function PersonalityPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "personality"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/personality"),
    refetchInterval: 10000,
  });
  const personality = (data?.personality as Record<string, unknown>) ?? {};
  const traits = (personality.traits as string[]) ?? [];
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Personality Projection</h2>
      <Card>
        <CardHeader title="Traits" subtitle={traits.join(", ") || "precise, supportive, curious"} />
        <CardBody>
          <p className="text-xs text-slate-400">Bounded personality continuity — transparent simulation.</p>
        </CardBody>
      </Card>
    </div>
  );
}
