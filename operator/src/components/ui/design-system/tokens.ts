/** Odin cinematic design tokens — single source of truth for Phase 9 UI system. */

export const odinColors = {
  bg: {
    deep: "#050608",
    base: "#07090f",
    elevated: "#0a0e16",
    panel: "#0d111c",
  },
  primary: {
    DEFAULT: "#22d3ee",
    dim: "#0891b2",
    glow: "rgba(34, 211, 238, 0.35)",
  },
  intelligence: {
    DEFAULT: "#38bdf8",
    field: "rgba(56, 189, 248, 0.12)",
  },
  success: {
    DEFAULT: "#34d399",
    muted: "rgba(52, 211, 153, 0.15)",
  },
  warning: {
    DEFAULT: "#d4a853",
    muted: "rgba(212, 168, 83, 0.15)",
  },
  error: {
    DEFAULT: "#e87986",
    muted: "rgba(232, 121, 134, 0.15)",
  },
  border: {
    DEFAULT: "rgba(255, 255, 255, 0.06)",
    strong: "rgba(255, 255, 255, 0.1)",
  },
  text: {
    primary: "#e2e8f0",
    secondary: "#94a3b8",
    muted: "#64748b",
    ghost: "#475569",
  },
} as const;

export const odinMotion = {
  duration: {
    fast: 0.15,
    normal: 0.28,
    slow: 0.65,
    system: 0.8,
  },
  ease: {
    intelligence: [0.22, 1, 0.36, 1] as [number, number, number, number],
    enter: [0.16, 1, 0.3, 1] as [number, number, number, number],
    exit: [0.4, 0, 0.2, 1] as [number, number, number, number],
  },
} as const;

export const odinSurfaces = {
  glass: {
    blur: "12px",
    bg: "rgba(13, 17, 28, 0.72)",
    border: odinColors.border.DEFAULT,
  },
  depth: {
    ambient: 0,
    panel: 10,
    overlay: 20,
    command: 30,
    orb: 40,
  },
} as const;

export const odinTypography = {
  missionTitle: "text-base font-semibold tracking-tight text-slate-100",
  systemState: "text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500",
  streamLog: "font-mono text-xs leading-relaxed text-slate-400",
  streamTime: "font-mono text-[10px] tabular-nums text-slate-600",
  signalKind: "text-[10px] font-medium uppercase tracking-wide",
} as const;
