"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";

export function MetricTile({
  label,
  value,
  sub,
  trend,
  alert,
}: {
  label: string;
  value: string | number;
  sub?: string;
  trend?: "up" | "down" | "neutral";
  alert?: boolean;
}) {
  return (
    <motion.div
      layout
      className={cn(
        "rounded-lg border border-odin-border bg-odin-bg/60 px-3 py-2.5",
        alert && "border-rose-500/40 bg-rose-500/5"
      )}
    >
      <p className="text-[10px] font-medium uppercase tracking-widest text-odin-muted">{label}</p>
      <p className={cn("mt-1 font-mono text-xl font-semibold text-slate-100", alert && "text-rose-400")}>
        {value}
      </p>
      {sub && <p className="mt-0.5 text-[10px] text-odin-muted">{sub}</p>}
      {trend && trend !== "neutral" && (
        <span className={cn("text-[10px]", trend === "up" ? "text-emerald-400" : "text-rose-400")}>
          {trend === "up" ? "▲" : "▼"}
        </span>
      )}
    </motion.div>
  );
}
