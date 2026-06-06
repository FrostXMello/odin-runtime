"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { runtimeApi } from "@/lib/api/runtime";
import { ApiError } from "@/lib/api/client";
import { GlassPanel } from "@/components/ui/design-system";
import {
  commandGlowStyle,
  transitionFast,
} from "@/components/ui/design-system/motion";
import type { OdinCorePhase } from "@/components/odin-core/odin-core-state";
import { cn } from "@/lib/utils/cn";

type Props = {
  onMissionCreated: (missionId: string) => void;
  onChatResponse?: (message: string) => void;
  onSystemResponse?: (message: string) => void;
  onFocusChange?: (focused: boolean) => void;
  onTypingChange?: (typing: boolean) => void;
  onCreatingChange?: (creating: boolean) => void;
  onTypingRipple?: () => void;
  onSubmitPulse?: () => void;
  focused?: boolean;
  orbPhase?: OdinCorePhase;
  typing?: boolean;
};

const PHASE_GLOW: Record<OdinCorePhase, number> = {
  idle: 0.15,
  listening: 0.55,
  thinking: 0.45,
  executing: 0.35,
  responding: 0.5,
  error: 0.25,
  completed: 0.2,
};

export function MissionCommandBar({
  onMissionCreated,
  onChatResponse,
  onSystemResponse,
  onFocusChange,
  onTypingChange,
  onCreatingChange,
  onTypingRipple,
  onSubmitPulse,
  focused: inputFocused,
  orbPhase = "idle",
  typing = false,
}: Props) {
  const qc = useQueryClient();
  const [command, setCommand] = useState("");
  const [error, setError] = useState<string | null>(null);

  const glowIntensity =
    (inputFocused ? PHASE_GLOW.listening : PHASE_GLOW[orbPhase]) + (typing ? 0.12 : 0);

  const create = useMutation({
    mutationFn: (text: string) =>
      runtimeApi.createMission({ objective: text.trim(), start_worker: true }),
    onMutate: () => {
      onCreatingChange?.(true);
      onSubmitPulse?.();
    },
    onSuccess: (result) => {
      setCommand("");
      setError(null);
      onCreatingChange?.(false);
      if (result.intent === "chat") {
        onChatResponse?.(result.message ?? "I'm here.");
        return;
      }
      if (result.intent === "system") {
        onSystemResponse?.(result.message ?? "System status retrieved.");
        return;
      }
      if (result.mission?.mission_id) {
        qc.invalidateQueries({ queryKey: ["missions"] });
        onMissionCreated(result.mission.mission_id);
      }
    },
    onError: (err: unknown) => {
      onCreatingChange?.(false);
      if (err instanceof ApiError) {
        if (err.status === 409) {
          setError("Similar mission already exists — try a different command.");
          return;
        }
        setError(err.message.slice(0, 160) || "Command failed");
        return;
      }
      setError("Command failed — is the Odin API running?");
    },
  });

  function submitCommand() {
    const text = command.trim();
    if (text.length < 3) {
      setError("Type at least 3 characters, then press Enter or Execute.");
      return;
    }
    if (create.isPending) return;
    create.mutate(text);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    submitCommand();
  }

  return (
    <motion.div animate={{ opacity: 1 }} transition={transitionFast}>
      <GlassPanel
        depth="command"
        glow={inputFocused || typing}
        glowStyle={commandGlowStyle(glowIntensity)}
        className={cn(
          inputFocused && "ring-1 ring-odin-cyan/15",
          typing && "ring-odin-cyan/10"
        )}
      >
        <form onSubmit={handleSubmit} className="flex items-center gap-3 px-4 py-3">
          <motion.span
            animate={{ opacity: inputFocused ? 1 : 0.5 }}
            transition={transitionFast}
            className="font-mono text-sm text-odin-cyan/70"
          >
            ›
          </motion.span>
          <input
            type="text"
            value={command}
            disabled={create.isPending}
            onChange={(e) => {
              setCommand(e.target.value);
              setError(null);
              const isTyping = e.target.value.length > 0;
              onTypingChange?.(isTyping);
              if (isTyping) onTypingRipple?.();
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                submitCommand();
              }
            }}
            onFocus={() => onFocusChange?.(true)}
            onBlur={() => {
              onFocusChange?.(false);
              onTypingChange?.(false);
            }}
            placeholder="Speak to the system…"
            className="min-w-0 flex-1 bg-transparent text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none"
            autoFocus
          />
          <button
            type="submit"
            disabled={create.isPending}
            className="shrink-0 rounded-lg bg-odin-cyan/12 px-4 py-1.5 text-xs font-medium text-odin-cyan ring-1 ring-odin-cyan/20 transition hover:bg-odin-cyan/20 disabled:cursor-wait disabled:opacity-50"
          >
            {create.isPending ? "Absorbing…" : "Execute"}
          </button>
        </form>
        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="border-t border-white/[0.04] px-4 py-2 text-xs text-odin-rose/90"
          >
            {error}
          </motion.p>
        )}
        {!error && command.trim().length > 0 && command.trim().length < 3 && (
          <p className="border-t border-white/[0.04] px-4 py-1.5 text-[10px] text-slate-600">
            {3 - command.trim().length} more character(s) to execute
          </p>
        )}
      </GlassPanel>
    </motion.div>
  );
}
