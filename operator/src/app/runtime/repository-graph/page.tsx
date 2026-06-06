"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RepositoryGraphPage() {
  const analyze = useMutation({
    mutationFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/repository-graph/analyze", {
        method: "POST",
        body: { repo: "odin", files: ["core/app.py", "api/main.py", "tests/test_x.py"] },
      }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Repository Graph</h2>
      <Card>
        <CardHeader title="Topology explorer" subtitle="Multi-file reasoning map" />
        <CardBody>
          <button type="button" className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => analyze.mutate()}>
            Analyze sample repo
          </button>
        </CardBody>
      </Card>
    </div>
  );
}
