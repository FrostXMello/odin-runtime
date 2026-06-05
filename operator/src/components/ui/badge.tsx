import { cn } from "@/lib/utils/cn";

const variants = {
  healthy: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  degraded: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  critical: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  default: "bg-odin-border/50 text-slate-300 border-odin-border",
  cyan: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
};

export function Badge({
  children,
  variant = "default",
  className,
  pulse,
}: {
  children: React.ReactNode;
  variant?: keyof typeof variants;
  className?: string;
  pulse?: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium uppercase tracking-wide",
        variants[variant],
        pulse && "animate-pulse-slow",
        className
      )}
    >
      {children}
    </span>
  );
}
