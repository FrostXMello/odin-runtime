"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { runtimeApi } from "@/lib/api/runtime";
import { ApiError } from "@/lib/api/client";
import { GlassPanel } from "@/components/ui/design-system";
import {
  commandGlowStyle,
  easeIntelligence,
  microPress,
  transitionFast,
} from "@/components/ui/design-system/motion";
import type { OdinCorePhase } from "@/components/odin-core/odin-core-state";
import { cn } from "@/lib/utils/cn";

type Props = {
  onMissionCreated: (missionId: string) => void;
  disabled?: boolean;
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
  disabled,
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
    <motion.div
      animate={{ opacity: 1 }}
      transition={transitionFast}
    >
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
            disabled={disabled || create.isPending}
            onChange={(e) => {
              setCommand(e.target.value);
              setError(null);
              const isTyping = e.target.value.length > 0;
              onTypingChange?.(isTyping);
              if (isTyping) onTypingRipple?.();
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
          <motion.button
            type="submit"
            disabled={disabled || create.isPending || command.trim().length < 3}
            {...microPress}
            className="shrink-0 rounded-lg bg-odin-cyan/12 px-4 py-1.5 text-xs font-medium text-odin-cyan ring-1 ring-odin-cyan/20 hover:bg-odin-cyan/20 disabled:cursor-not-allowed disabled:opacity-30"
          >
            {create.isPending ? "Absorbing…" : "Execute"}
          </motion.button>
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
      </GlassPanel>
    </motion.div>
  );
}
