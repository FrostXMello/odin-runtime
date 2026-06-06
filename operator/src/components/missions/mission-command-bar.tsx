"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { runtimeApi } from "@/lib/api/runtime";
import { ApiError } from "@/lib/api/client";
import { Terminal } from "lucide-react";

type Props = {
  onMissionCreated: (missionId: string) => void;
  disabled?: boolean;
  onFocusChange?: (focused: boolean) => void;
  onTypingChange?: (typing: boolean) => void;
  onCreatingChange?: (creating: boolean) => void;
};

export function MissionCommandBar({
  onMissionCreated,
  disabled,
  onFocusChange,
  onTypingChange,
  onCreatingChange,
}: Props) {
  const qc = useQueryClient();
  const [command, setCommand] = useState("");
  const [error, setError] = useState<string | null>(null);

  const create = useMutation({
    mutationFn: (text: string) =>
      runtimeApi.createMission({ objective: text.trim(), start_worker: true }),
    onMutate: () => onCreatingChange?.(true),
    onSuccess: (mission) => {
      setCommand("");
      setError(null);
      onCreatingChange?.(false);
      qc.invalidateQueries({ queryKey: ["missions"] });
      onMissionCreated(mission.mission_id);
    },
    onError: (err: unknown) => {
      onCreatingChange?.(false);
      if (err instanceof ApiError) {
        setError(err.message.slice(0, 160) || "Command failed");
        return;
      }
      setError("Command failed");
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = command.trim();
    if (text.length < 3) {
      setError("Enter a mission command (min 3 characters).");
      return;
    }
    create.mutate(text);
  }

  return (
    <div className="rounded-xl border border-odin-border/80 bg-odin-panel/90 shadow-panel">
      <form onSubmit={handleSubmit} className="flex items-center gap-2 px-3 py-2">
        <Terminal className="h-4 w-4 shrink-0 text-odin-cyan" aria-hidden />
        <span className="font-mono text-sm text-odin-cyan/90">›</span>
        <input
          type="text"
          value={command}
          disabled={disabled || create.isPending}
          onChange={(e) => {
            setCommand(e.target.value);
            setError(null);
            onTypingChange?.(e.target.value.length > 0);
          }}
          onFocus={() => onFocusChange?.(true)}
          onBlur={() => {
            onFocusChange?.(false);
            onTypingChange?.(false);
          }}
          placeholder="Enter mission command..."
          className="min-w-0 flex-1 bg-transparent font-mono text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
          autoFocus
        />
        <button
          type="submit"
          disabled={disabled || create.isPending || command.trim().length < 3}
          className="shrink-0 rounded-md bg-odin-accent/90 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-odin-accent disabled:cursor-not-allowed disabled:opacity-40"
        >
          {create.isPending ? "Exec…" : "Run"}
        </button>
      </form>
      {error && <p className="border-t border-odin-border/40 px-3 py-1.5 text-xs text-rose-400">{error}</p>}
    </div>
  );
}
