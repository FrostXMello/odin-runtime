"use client";

import { cn } from "@/lib/utils/cn";
import { motion, type Transition } from "framer-motion";
import type { ReactNode } from "react";
import { layerDominance, layerDominanceTransition } from "./motion";

type GlassProps = {
  children: ReactNode;
  className?: string;
  depth?: "ambient" | "panel" | "command" | "stream";
  glow?: boolean;
  glowStyle?: React.CSSProperties;
};

const depthClasses = {
  ambient: "bg-odin-graphite/40 border-white/[0.04]",
  panel: "bg-odin-glass border-white/[0.06] backdrop-blur-md",
  command: "bg-odin-glass-strong border-white/[0.08] backdrop-blur-lg shadow-odin-command",
  stream: "bg-odin-glass border-white/[0.05] backdrop-blur-md shadow-odin-panel",
};

export function GlassPanel({ children, className, depth = "panel", glow, glowStyle }: GlassProps) {
  return (
    <div
      className={cn("rounded-2xl border", depthClasses[depth], glow && "shadow-odin-glow", className)}
      style={glowStyle}
    >
      {children}
    </div>
  );
}

export type LayerDominance = keyof typeof layerDominance;

export function SurfaceLayer({
  children,
  className,
  z = "execution",
  dominance = "active",
}: {
  children: ReactNode;
  className?: string;
  z?: "identity" | "command" | "execution" | "archive";
  dominance?: LayerDominance;
}) {
  const zIndex = { identity: "z-10", command: "z-20", execution: "z-30", archive: "z-0" };
  return (
    <motion.section
      className={cn("relative", zIndex[z], className)}
      animate={layerDominance[dominance]}
      transition={layerDominanceTransition as Transition}
    >
      {children}
    </motion.section>
  );
}
