"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useStreamStore } from "@/store/stream-store";

export function ActivityTicker() {
  const ticker = useStreamStore((s) => s.ticker);

  if (!ticker.length) return null;

  return (
    <div className="overflow-hidden border-b border-odin-border/60 bg-odin-bg/80">
      <div className="flex items-center gap-2 px-4 py-1.5">
        <span className="shrink-0 text-[9px] font-bold tracking-widest text-odin-cyan">ACTIVITY</span>
        <div className="flex min-w-0 flex-1 gap-4 overflow-x-auto">
          <AnimatePresence mode="popLayout">
            {ticker.slice(0, 8).map((ev) => (
              <motion.div
                key={ev.event_id}
                layout
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex shrink-0 items-center gap-2 font-mono text-[10px] text-slate-400"
              >
                <span className="uppercase text-odin-muted">{ev.event_type}</span>
                <span className="max-w-[200px] truncate text-slate-300">{ev.message}</span>
                {ev.mission_id && (
                  <Link href={`/missions/${ev.mission_id}`} className="text-odin-cyan hover:underline">
                    {ev.mission_id.slice(0, 8)}
                  </Link>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
