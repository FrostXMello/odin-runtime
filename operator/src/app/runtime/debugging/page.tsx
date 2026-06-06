"use client";

import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function DebuggingPage() {
  const assist = useMutation({
    mutationFn: () =>
      apiFetch<Record<string, unknown>>("/runtime/debugging/assist", {
        method: "POST",
        body: { error: "ImportError: module not found", context: { test_failure: true } },
      }),
  });
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Debugging Assistant</h2>
      <Card>
        <CardHeader title="Debug workflows" subtitle="Context-aware bug localization" />
        <CardBody>
          <button type="button" className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan" onClick={() => assist.mutate()}>
            Run sample debug assist
          </button>
        </CardBody>
      </Card>
    </div>
  );
}
