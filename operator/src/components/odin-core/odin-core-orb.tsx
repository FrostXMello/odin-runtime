"use client";

import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import { odinTypography } from "@/components/ui/design-system";
import {
  easeIntelligence,
  orbBreath,
  transitionOrbMorph,
  transitionOrbInstant,
  orbAbsorb,
  orbCompletePulse,
} from "@/components/ui/design-system/motion";
import type { MotionTier } from "@/hooks/useVisualPerformance";
import { phaseLabel, type OdinCorePhase } from "@/components/odin-core/odin-core-state";
import { orbColorForPhase, orbMorphForPhase } from "@/components/odin-core/orb-morph";

type Props = {
  phase: OdinCorePhase;
  motionTier?: MotionTier;
  pulseKey?: number;
  typingRippleKey?: number;
  absorbKey?: number;
  activityIntensity?: number;
  compact?: boolean;
  className?: string;
};

export function OdinCoreOrb({
  phase,
  motionTier = "full",
  pulseKey = 0,
  typingRippleKey = 0,
  absorbKey = 0,
  activityIntensity = 0,
  compact = false,
  className,
}: Props) {
  const size = compact ? 44 : 64;
  const color = orbColorForPhase(phase);
  const morph = orbMorphForPhase(phase, activityIntensity);
  const physics = motionTier === "full";
  const breath = orbBreath[motionTier];

  return (
    <div className={cn("relative flex flex-col items-center", className)} aria-hidden>
      <div
        className="odin-orb-projection pointer-events-none absolute left-1/2 top-full h-20 w-52 -translate-x-1/2"
        style={{ opacity: 0.25 + activityIntensity * 0.35 + morph.fieldOpacity * 0.3 }}
      />

      <div className="relative" style={{ width: size + 52, height: size + 52 }}>
        {/* Continuous breathing field — always on */}
        <motion.div
          className="absolute inset-0 rounded-full"
          animate={{
            opacity: [morph.fieldOpacity * 0.85, morph.fieldOpacity, morph.fieldOpacity * 0.85],
            scale: [morph.fieldScale * 0.98, morph.fieldScale, morph.fieldScale * 0.98],
            background: `radial-gradient(circle, ${color}22 0%, transparent 72%)`,
          }}
          transition={{
            opacity: { duration: motionTier === "minimal" ? 5 : 4, repeat: Infinity, ease: easeIntelligence },
            scale: { duration: motionTier === "minimal" ? 5 : 4, repeat: Infinity, ease: easeIntelligence },
            background: transitionOrbMorph,
          }}
        />

        {/* Morphing aura — crossfades with phase */}
        <motion.div
          className="absolute inset-2 rounded-full border border-white/[0.04]"
          animate={{
            boxShadow: `0 0 ${morph.glowSpread}px -14px ${color}55`,
            ...breath,
          }}
          transition={{
            boxShadow: transitionOrbMorph,
            scale: { duration: 4.2, repeat: Infinity, ease: easeIntelligence },
            opacity: { duration: 4.2, repeat: Infinity, ease: easeIntelligence },
          }}
        />

        {/* Activity-synced ambient pulse */}
        {activityIntensity > 0.15 && (
          <motion.div
            className="absolute inset-4 rounded-full"
            style={{ background: `radial-gradient(circle, ${color}12, transparent 70%)` }}
            animate={{ opacity: [0.15, 0.15 + activityIntensity * 0.35, 0.15] }}
            transition={{ duration: 1.2 + (1 - activityIntensity) * 0.8, repeat: Infinity, ease: easeIntelligence }}
          />
        )}

        {/* Typing signal ripple → orb */}
        <AnimatePresence>
          {typingRippleKey > 0 && physics && (
            <motion.div
              key={`type-${typingRippleKey}`}
              className="absolute inset-3 rounded-full border border-cyan-400/15"
              initial={{ scale: 0.85, opacity: 0.4 }}
              animate={{ scale: 1.15, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.55, ease: easeIntelligence }}
            />
          )}
        </AnimatePresence>

        {/* Stream response ripple */}
        <AnimatePresence>
          {pulseKey > 0 && (
            <motion.div
              key={`pulse-${pulseKey}`}
              className="absolute inset-0 rounded-full border"
              style={{ borderColor: `${color}33` }}
              initial={{ scale: 0.7, opacity: physics ? 0.45 : 0.25 }}
              animate={{ scale: 1.25, opacity: 0 }}
              transition={{ duration: physics ? 0.75 : 0.5, ease: easeIntelligence }}
            />
          )}
        </AnimatePresence>

        {/* Command absorb */}
        <AnimatePresence>
          {absorbKey > 0 && (
            <motion.div
              key={`absorb-${absorbKey}`}
              className="absolute inset-0 flex items-center justify-center"
              variants={orbAbsorb}
              initial="idle"
              animate="absorb"
            >
              <div className="h-full w-full rounded-full bg-cyan-400/08" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Completion golden pulse */}
        {phase === "completed" && (
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{ background: "radial-gradient(circle, rgba(252,211,77,0.2), transparent 70%)" }}
            variants={orbCompletePulse}
            initial="idle"
            animate="pulse"
          />
        )}

        {/* Error — soft bloom, not flash */}
        {phase === "error" && (
          <motion.div
            className="absolute inset-0 rounded-full bg-odin-rose/08"
            animate={{ opacity: [0.08, 0.18, 0.1] }}
            transition={{ duration: 3.2, repeat: Infinity, ease: easeIntelligence }}
          />
        )}

        {/* Core sphere — fluid morph */}
        <motion.div
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full shadow-odin-orb"
          style={{ width: size, height: size }}
          animate={{
            scale: morph.scale,
            opacity: morph.coreOpacity,
            background: `radial-gradient(circle at 38% 32%, ${color}cc, ${color}55 44%, #0a0e16 100%)`,
            boxShadow: `0 0 ${morph.glowSpread}px -12px ${color}44, inset 0 -8px 16px rgba(0,0,0,0.35)`,
          }}
          transition={phase === "listening" ? transitionOrbInstant : transitionOrbMorph}
        >
          <div
            className="absolute inset-[20%] rounded-full"
            style={{
              background: "radial-gradient(circle at 42% 38%, rgba(255,255,255,0.32), transparent 60%)",
            }}
          />
          {physics && phase === "thinking" && (
            <motion.div
              className="absolute inset-[30%] rounded-full opacity-25"
              style={{ background: `conic-gradient(from 0deg, transparent, ${color}66, transparent)` }}
              animate={{ rotate: 360 }}
              transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
            />
          )}
        </motion.div>

        {physics && phase === "listening" && <DriftParticles color={color} />}
      </div>

      {!compact && (
        <motion.p
          key={phase}
          animate={{ opacity: 1 }}
          initial={{ opacity: 0.6 }}
          transition={transitionOrbMorph}
          className={cn("mt-3", odinTypography.systemState)}
        >
          {phaseLabel(phase)}
        </motion.p>
      )}
    </div>
  );
}

function DriftParticles({ color }: { color: string }) {
  return (
    <>
      {[
        { x: -20, y: -4, delay: 0 },
        { x: 22, y: 2, delay: 0.6 },
      ].map((p, i) => (
        <motion.span
          key={i}
          className="absolute left-1/2 top-1/2 h-0.5 w-0.5 rounded-full"
          style={{ backgroundColor: color }}
          animate={{ x: [0, p.x], y: [0, p.y], opacity: [0.4, 0] }}
          transition={{ duration: 2.8, repeat: Infinity, delay: p.delay, ease: easeIntelligence }}
        />
      ))}
    </>
  );
}

export function OdinCoreMini({ phase }: { phase: OdinCorePhase }) {
  const color = orbColorForPhase(phase);
  return (
    <motion.span
      className="inline-block h-1.5 w-1.5 shrink-0 rounded-full"
      style={{ backgroundColor: color }}
      animate={{ opacity: phase === "idle" ? 0.45 : 0.8 }}
      transition={{ duration: 0.28, ease: easeIntelligence }}
      title={phaseLabel(phase)}
    />
  );
}
