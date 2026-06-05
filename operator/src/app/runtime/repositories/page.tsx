"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardHeader } from "@/components/ui/card";

export default function RepositoriesPage() {
  const { data } = useQuery({ queryKey: ["runtime", "repositories"], queryFn: () => apiFetch("/runtime/repositories") });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Repositories</h2>
      <Card><CardHeader title="Repo activity" subtitle="Git read-only observer" /></Card>
    </div>
  );
}
