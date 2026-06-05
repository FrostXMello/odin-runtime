import { motion } from "framer-motion";
import { OdinEvent } from "@/lib/api";

export function EventStream({ events }: { events: OdinEvent[] }) {
  if (!events.length) {
    return <p className="text-odin-muted text-sm">Waiting for events…</p>;
  }

  return (
    <div className="space-y-2 font-mono text-xs max-h-[480px] overflow-y-auto">
      {events.map((e) => (
        <motion.div
          key={`${e.id}-${e.timestamp}`}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          className="rounded border border-odin-border bg-odin-bg px-3 py-2"
        >
          <div className="flex gap-2 text-odin-accent">
            <span>{e.type}</span>
            <span className="text-odin-muted">·</span>
            <span className="text-slate-400">{e.source}</span>
          </div>
          <div className="text-odin-muted mt-1 truncate">
            {new Date(e.timestamp).toLocaleTimeString()}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
