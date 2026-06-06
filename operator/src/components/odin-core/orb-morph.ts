import type { OdinCorePhase } from "@/components/odin-core/odin-core-state";
import { phaseColor } from "@/components/odin-core/odin-core-state";

export type OrbMorphTarget = {
  scale: number;
  fieldOpacity: number;
  fieldScale: number;
  glowSpread: number;
  coreOpacity: number;
};

export function orbMorphForPhase(phase: OdinCorePhase, intensity: number): OrbMorphTarget {
  const boost = 1 + intensity * 0.12;
  switch (phase) {
    case "idle":
      return { scale: 1, fieldOpacity: 0.22, fieldScale: 1.02, glowSpread: 36, coreOpacity: 0.82 };
    case "listening":
      return { scale: 1.04 * boost, fieldOpacity: 0.38, fieldScale: 1.08, glowSpread: 44, coreOpacity: 0.94 };
    case "thinking":
      return { scale: 0.97, fieldOpacity: 0.42, fieldScale: 1.05, glowSpread: 48, coreOpacity: 0.9 };
    case "executing":
      return { scale: 1.03 * boost, fieldOpacity: 0.35 + intensity * 0.15, fieldScale: 1.06, glowSpread: 42 + intensity * 12, coreOpacity: 0.92 };
    case "responding":
      return { scale: 1.06, fieldOpacity: 0.48, fieldScale: 1.1, glowSpread: 52, coreOpacity: 1 };
    case "error":
      return { scale: 0.99, fieldOpacity: 0.28, fieldScale: 1.01, glowSpread: 32, coreOpacity: 0.86 };
    case "completed":
      return { scale: 1.01, fieldOpacity: 0.32, fieldScale: 1.03, glowSpread: 40, coreOpacity: 0.78 };
  }
}

export function orbColorForPhase(phase: OdinCorePhase): string {
  return phaseColor(phase);
}
