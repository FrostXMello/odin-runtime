"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function CognitionLivePage() {
  const { data } = useQuery({
    queryKey: ["runtime", "cognition-live"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/cognition-live"),
    refetchInterval: 5000,
  });
  const shell = (data?.shell as Record<string, unknown>) ?? {};
  const ui = (shell.ui as Record<string, unknown>) ?? {};
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Live Cognition Viewport</h2>
      <Card>
        <CardHeader title="UI Mode" subtitle={String(ui.mode ?? "balanced")} />
        <CardBody>
          <p className="text-xs text-slate-400">FPS target: {String(ui.fps_target ?? 30)}</p>
          <p className="text-xs text-slate-500">Native desktop layer · unified with immersive UI</p>
        </CardBody>
      </Card>
    </div>
  );
}
