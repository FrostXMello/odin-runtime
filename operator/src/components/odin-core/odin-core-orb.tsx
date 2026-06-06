"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import {
  phaseColor,
  phaseLabel,
  type OdinCorePhase,
} from "@/components/odin-core/odin-core-state";

type Props = {
  phase: OdinCorePhase;
  animationsEnabled: boolean;
  pulseKey?: number;
  compact?: boolean;
  className?: string;
};

export function OdinCoreOrb({ phase, animationsEnabled, pulseKey = 0, compact = false, className }: Props) {
  const color = phaseColor(phase);
  const size = compact ? 48 : 72;

  if (!animationsEnabled) {
    return (
      <div className={cn("flex flex-col items-center", className)}>
        <StaticOrb phase={phase} size={size} />
        {!compact && (
          <p className="mt-2 font-mono text-[10px] uppercase tracking-widest text-slate-500">
            {phaseLabel(phase)}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col items-center", className)} aria-hidden>
      <div className="relative" style={{ width: size + 40, height: size + 40 }}>
        {phase === "listening" && (
          <motion.div
            className="absolute inset-0 rounded-full border border-cyan-400/30"
            animate={{ scale: [1, 1.12, 1], opacity: [0.35, 0.65, 0.35] }}
            transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
          />
        )}

        {(phase === "executing" || phase === "responding") && (
          <>
            <motion.div
              className="absolute inset-2 rounded-full border border-cyan-400/20"
              animate={{ scale: [0.85, 1.15], opacity: [0.5, 0] }}
              transition={{ duration: 2.2, repeat: Infinity, ease: "easeOut" }}
            />
            <motion.div
              className="absolute inset-4 rounded-full border border-cyan-400/15"
              animate={{ scale: [0.9, 1.2], opacity: [0.35, 0] }}
              transition={{ duration: 2.2, repeat: Infinity, ease: "easeOut", delay: 0.6 }}
            />
          </>
        )}

        {phase === "responding" && pulseKey > 0 && (
          <motion.div
            key={pulseKey}
            className="absolute inset-0 rounded-full border-2"
            style={{ borderColor: `${color}66` }}
            initial={{ scale: 0.6, opacity: 0.7 }}
            animate={{ scale: 1.35, opacity: 0 }}
            transition={{ duration: 0.65, ease: "easeOut" }}
          />
        )}

        {phase === "thinking" && (
          <motion.div
            className="absolute inset-3 rounded-full opacity-40"
            style={{
              background: `conic-gradient(from 0deg, transparent, ${color}, transparent)`,
            }}
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          />
        )}

        {phase === "error" && (
          <motion.div
            className="absolute inset-0 rounded-full bg-rose-500/20"
            animate={{ opacity: [0.15, 0.35, 0.2, 0.3, 0.15] }}
            transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
          />
        )}

        {phase === "completed" && (
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{
              background: "radial-gradient(circle, rgba(252,211,77,0.25) 0%, transparent 70%)",
            }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: [0, 0.8, 0.3], scale: [0.8, 1.1, 1] }}
            transition={{ duration: 2, ease: "easeOut" }}
          />
        )}

        <motion.div
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full"
          style={{
            width: size,
            height: size,
            background: `radial-gradient(circle at 35% 35%, ${color}ee, ${color}88 45%, #1e293b 100%)`,
            boxShadow: `0 0 ${compact ? 24 : 36}px -8px ${color}88`,
          }}
          animate={orbMotion(phase)}
          transition={orbTransition(phase)}
        >
          <div
            className="absolute inset-[18%] rounded-full opacity-60"
            style={{
              background: `radial-gradient(circle at 40% 35%, rgba(255,255,255,0.45), transparent 65%)`,
            }}
          />
        </motion.div>

        {phase === "listening" && <DriftParticles color={color} />}
        {phase === "executing" && (
          <motion.div
            className="absolute left-1/2 top-1/2 h-1 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300/80"
            animate={{ x: [0, 1, -1, 0], y: [0, -1, 1, 0] }}
            transition={{ duration: 0.12, repeat: Infinity, repeatDelay: 1.8 }}
          />
        )}
      </div>
      {!compact && (
        <motion.p
          key={phase}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-2 font-mono text-[10px] uppercase tracking-widest text-slate-500"
        >
          {phaseLabel(phase)}
        </motion.p>
      )}
    </div>
  );
}

function StaticOrb({ phase, size }: { phase: OdinCorePhase; size: number }) {
  const color = phaseColor(phase);
  return (
    <div
      className="rounded-full"
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle at 35% 35%, ${color}cc, ${color}66 50%, #1e293b 100%)`,
        boxShadow: `0 0 20px -6px ${color}55`,
        opacity: phase === "idle" ? 0.75 : 1,
      }}
    />
  );
}

function DriftParticles({ color }: { color: string }) {
  const offsets = [
    { x: -28, y: -8, delay: 0 },
    { x: 30, y: 4, delay: 0.4 },
    { x: -6, y: 32, delay: 0.8 },
  ];
  return (
    <>
      {offsets.map((p, i) => (
        <motion.span
          key={i}
          className="absolute left-1/2 top-1/2 h-1 w-1 rounded-full"
          style={{ backgroundColor: color }}
          initial={{ x: 0, y: 0, opacity: 0.5 }}
          animate={{ x: p.x, y: p.y, opacity: [0.5, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, delay: p.delay, ease: "easeOut" }}
        />
      ))}
    </>
  );
}

function orbMotion(phase: OdinCorePhase) {
  switch (phase) {
    case "idle":
      return { scale: [1, 1.04, 1], opacity: [0.75, 0.9, 0.75] };
    case "listening":
      return { scale: [1, 1.06, 1], rotate: [0, 4, -4, 0] };
    case "thinking":
      return { scale: [0.94, 1.06, 0.96, 1] };
    case "executing":
      return { scale: [1, 1.05, 1] };
    case "responding":
      return { scale: [1, 1.12, 1] };
    case "error":
      return { scale: [1, 0.98, 1.01, 1], opacity: [0.85, 0.95, 0.8, 0.85] };
    case "completed":
      return { scale: [1, 1.02, 1], opacity: [1, 0.85, 0.75] };
  }
}

function orbTransition(phase: OdinCorePhase) {
  const slow = { duration: 3.2, repeat: Infinity, ease: "easeInOut" as const };
  switch (phase) {
    case "idle":
      return slow;
    case "listening":
      return { duration: 2.8, repeat: Infinity, ease: "easeInOut" };
    case "thinking":
      return { duration: 1.8, repeat: Infinity, ease: "easeInOut" };
    case "executing":
      return { duration: 1.6, repeat: Infinity, ease: "easeInOut" };
    case "responding":
      return { duration: 0.45, ease: "easeOut" };
    case "error":
      return { duration: 2.5, repeat: Infinity, ease: "easeInOut" };
    case "completed":
      return { duration: 2, ease: "easeOut" };
  }
}

/** Static mini indicator for completed mission rows (performance mode only). */
export function OdinCoreMini({ phase }: { phase: OdinCorePhase }) {
  const color = phaseColor(phase);
  return (
    <span
      className="inline-block h-2 w-2 shrink-0 rounded-full"
      style={{ backgroundColor: color, opacity: phase === "idle" ? 0.5 : 0.85 }}
      title={phaseLabel(phase)}
    />
  );
}
