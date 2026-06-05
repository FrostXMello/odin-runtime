"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeAutomationPage() {
  const { data } = useQuery({
    queryKey: ["runtime", "automation"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/automation"),
    refetchInterval: 5000,
  });
  const overlay = (data?.overlay as Record<string, unknown>) ?? {};

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Desktop automation</h2>
      <Card>
        <CardHeader title="Sandbox status" />
        <CardBody className="font-mono text-xs text-slate-400 space-y-1">
          <div>Simulation: {String(data?.simulation_mode ?? true)}</div>
          <div>Enabled: {String(data?.desktop_automation_enabled ?? false)}</div>
          <div>Overlay annotations: {((overlay.annotations as unknown[]) ?? []).length}</div>
        </CardBody>
      </Card>
    </div>
  );
}
