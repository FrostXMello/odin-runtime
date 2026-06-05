"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardHeader } from "@/components/ui/card";

export default function WorkspacesPage() {
  const { data } = useQuery({ queryKey: ["runtime", "knowledge-workspace"], queryFn: () => apiFetch("/runtime/knowledge-workspace") });
  const w = (data?.workspace as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Workspaces</h2>
      <Card><CardHeader title="Semantic workspace" subtitle={`${String(w.documents ?? 0)} documents`} /></Card>
    </div>
  );
}
