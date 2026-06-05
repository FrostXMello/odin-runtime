"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export default function RuntimeVoicePage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["runtime", "voice"],
    queryFn: () => apiFetch<Record<string, unknown>>("/runtime/voice"),
    refetchInterval: 5000,
  });

  const start = useMutation({
    mutationFn: () => apiFetch("/runtime/voice/start", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "voice"] }),
  });
  const stop = useMutation({
    mutationFn: () => apiFetch("/runtime/voice/stop", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime", "voice"] }),
  });

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-medium text-slate-200">Voice interface</h2>
      <div className="flex gap-2">
        <button
          className="rounded bg-odin-accent/20 px-3 py-1 text-xs text-odin-cyan"
          onClick={() => start.mutate()}
        >
          Start session
        </button>
        <button
          className="rounded bg-odin-border px-3 py-1 text-xs text-slate-300"
          onClick={() => stop.mutate()}
        >
          Stop session
        </button>
      </div>
      <Card>
        <CardHeader title="Voice monitor" subtitle="Local STT/TTS" />
        <CardBody className="font-mono text-xs text-slate-400">
          Active: {String(data?.active ?? false)} · Turns: {String(data?.turns ?? 0)}
        </CardBody>
      </Card>
    </div>
  );
}
