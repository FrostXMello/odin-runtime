"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardHeader } from "@/components/ui/card";

export default function TasksPage() {
  const { data } = useQuery({ queryKey: ["runtime", "tasks"], queryFn: () => apiFetch("/runtime/tasks") });
  const p = (data?.productivity as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Tasks</h2>
      <Card><CardHeader title="Open tasks" subtitle={`${String(p.open_tasks ?? 0)} open`} /></Card>
    </div>
  );
}
