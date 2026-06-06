import type { Transition, Variants } from "framer-motion";
import { odinMotion } from "./tokens";
import type { MotionTier } from "@/hooks/useVisualPerformance";

export const easeIntelligence = odinMotion.ease.intelligence;
export const easeEnter = odinMotion.ease.enter;
export const easeAware = [0.34, 0.72, 0.22, 1] as [number, number, number, number];

/** Micro-delay so orb feels aware, not reactive. */
export const ORB_AWARE_DELAY_S = 0.07;

export const transitionFast: Transition = {
  duration: odinMotion.duration.fast,
  ease: easeIntelligence,
};

export const transitionNormal: Transition = {
  duration: odinMotion.duration.normal,
  ease: easeIntelligence,
};

export const transitionSlow: Transition = {
  duration: odinMotion.duration.slow,
  ease: easeIntelligence,
};

export const transitionOrbMorph: Transition = {
  duration: odinMotion.duration.slow,
  ease: easeAware,
  delay: ORB_AWARE_DELAY_S,
};

export const transitionOrbInstant: Transition = {
  duration: odinMotion.duration.normal,
  ease: easeIntelligence,
};

/** Signal enters the stream — unified transmission feel. */
export const signalInject: Variants = {
  hidden: { opacity: 0, x: -8 },
  visible: {
    opacity: 1,
    x: 0,
    transition: transitionNormal,
  },
};

/** Signal at rest in the stream. */
export const signalPersist: Variants = {
  visible: { opacity: 0.72, x: 0 },
};

/** Latest signal — subtle pulse, not a flash. */
export const signalUpdate: Variants = {
  visible: {
    opacity: 1,
    x: 0,
    transition: transitionFast,
  },
  pulse: {
    opacity: [1, 0.92, 1],
    transition: { duration: 0.55, ease: easeIntelligence },
  },
};

/** Error bloom — soft, not harsh. */
export const signalError: Variants = {
  visible: {
    opacity: 1,
    x: 0,
    boxShadow: "0 0 0 rgba(232, 121, 134, 0)",
    transition: transitionNormal,
  },
  bloom: {
    boxShadow: [
      "0 0 0 rgba(232, 121, 134, 0)",
      "0 0 12px rgba(232, 121, 134, 0.12)",
      "0 0 0 rgba(232, 121, 134, 0)",
    ],
    transition: { duration: 1.2, ease: easeIntelligence },
  },
};

/** Opacity-only tier — UI stays alive, physics removed. */
export const signalMinimal: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: odinMotion.duration.fast } },
};

export function signalVariantsForTier(tier: MotionTier): Variants {
  if (tier === "full") return signalInject;
  return signalMinimal;
}

export const layerReveal: Variants = {
  hidden: { opacity: 0, y: 6 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: odinMotion.duration.normal, ease: easeEnter },
  },
};

/** Layer dominance — one cognitive focus at a time. */
export const layerDominance = {
  dominant: { opacity: 1, filter: "blur(0px)", scale: 1 },
  active: { opacity: 0.92, filter: "blur(0px)", scale: 1 },
  background: { opacity: 0.45, filter: "blur(0.5px)", scale: 0.995 },
  archive: { opacity: 0.38, filter: "blur(0px)", scale: 1 },
} as const;

export const layerDominanceTransition: Transition = {
  duration: odinMotion.duration.slow,
  ease: easeIntelligence,
};

export const orbBreath = {
  full: { scale: [1, 1.028, 1], opacity: [0.78, 0.92, 0.78] },
  reduced: { scale: [1, 1.014, 1], opacity: [0.85, 0.94, 0.85] },
  minimal: { scale: [1, 1.008, 1], opacity: [0.88, 0.96, 0.88] },
};

export const microHover = {
  whileHover: { opacity: 0.92 },
  transition: transitionFast,
};

export const microPress = {
  whileTap: { scale: 0.985 },
  transition: { duration: 0.1, ease: easeIntelligence },
};

export const orbAbsorb: Variants = {
  idle: { scale: 1 },
  absorb: {
    scale: [1, 0.94, 1.04, 1],
    transition: { duration: 0.75, ease: easeAware },
  },
};

export const orbCompletePulse: Variants = {
  idle: { opacity: 0 },
  pulse: {
    opacity: [0, 0.5, 0],
    scale: [0.9, 1.15, 1],
    transition: { duration: 1.8, ease: easeIntelligence },
  },
};

/** Command bar glow keyed to orb phase intensity 0–1. */
import type { CSSProperties } from "react";

export function commandGlowStyle(intensity: number): CSSProperties {
  const a = Math.min(1, Math.max(0, intensity));
  return {
    boxShadow: `0 0 ${24 + a * 32}px -8px rgba(34, 211, 238, ${0.08 + a * 0.18})`,
  };
}
