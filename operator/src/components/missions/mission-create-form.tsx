"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { ApiError } from "@/lib/api/client";
import { Card, CardBody, CardHeader } from "@/components/ui/card";

export function MissionCreateForm() {
  const router = useRouter();
  const qc = useQueryClient();
  const [objective, setObjective] = useState("");
  const [error, setError] = useState<string | null>(null);

  const create = useMutation({
    mutationFn: (text: string) =>
      runtimeApi.createMission({ objective: text.trim(), start_worker: true }),
    onSuccess: (mission) => {
      setObjective("");
      setError(null);
      qc.invalidateQueries({ queryKey: ["missions"] });
      router.push(`/missions/${mission.mission_id}`);
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError) {
        setError(err.message.slice(0, 200) || "Could not create mission");
        return;
      }
      setError("Could not create mission");
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = objective.trim();
    if (text.length < 3) {
      setError("Describe what you want Odin to do (at least a few words).");
      return;
    }
    create.mutate(text);
  }

  return (
    <Card glow>
      <CardHeader
        title="New mission"
        subtitle="Describe your goal — Odin plans and executes from here"
      />
      <CardBody>
        <form onSubmit={handleSubmit} className="space-y-3">
          <textarea
            value={objective}
            onChange={(e) => {
              setObjective(e.target.value);
              setError(null);
            }}
            placeholder="e.g. Review the auth module, list failing tests, and suggest fixes"
            rows={3}
            className="w-full resize-none rounded-lg border border-odin-border/60 bg-odin-bg/60 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500 focus:border-odin-cyan/50 focus:outline-none"
          />
          {error && <p className="text-xs text-rose-400">{error}</p>}
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={create.isPending || objective.trim().length < 3}
              className="rounded-lg bg-odin-accent/90 px-4 py-2 text-sm font-medium text-white transition hover:bg-odin-accent disabled:cursor-not-allowed disabled:opacity-40"
            >
              {create.isPending ? "Creating…" : "Create & run mission"}
            </button>
            <p className="text-[10px] text-odin-muted">Enter to submit · lands on mission detail</p>
          </div>
        </form>
      </CardBody>
    </Card>
  );
}
