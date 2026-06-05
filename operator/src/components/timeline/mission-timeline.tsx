"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ExternalLink } from "lucide-react";
import type { TimelineEntry } from "@/lib/api/types";
import { eventColor, matchesFilter, type EventFilter, EVENT_FILTERS } from "@/lib/timeline/event-meta";
import { cn } from "@/lib/utils/cn";

export function MissionTimelineView({
  entries,
  traceId,
  causalChainId,
}: {
  entries: TimelineEntry[];
  traceId?: string | null;
  causalChainId?: string | null;
}) {
  const [filter, setFilter] = useState<EventFilter>("all");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [sortDesc, setSortDesc] = useState(true);

  const filtered = useMemo(() => {
    let list = entries.filter((e) => matchesFilter(e.kind, filter));
    list = [...list].sort((a, b) =>
      sortDesc ? b.sort_key - a.sort_key : a.sort_key - b.sort_key
    );
    return list;
  }, [entries, filter, sortDesc]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {EVENT_FILTERS.map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-md border px-2 py-1 text-[10px] uppercase tracking-wide transition-colors",
              filter === f
                ? "border-odin-cyan/50 bg-odin-cyan/10 text-odin-cyan"
                : "border-odin-border text-odin-muted hover:text-slate-300"
            )}
          >
            {f}
          </button>
        ))}
        <button
          type="button"
          onClick={() => setSortDesc(!sortDesc)}
          className="ml-auto text-[10px] text-odin-muted hover:text-slate-300"
        >
          Sort: {sortDesc ? "newest" : "oldest"}
        </button>
      </div>

      {(traceId || causalChainId) && (
        <div className="flex flex-wrap gap-3 rounded-lg border border-odin-border/60 bg-odin-bg/50 px-3 py-2 font-mono text-[10px]">
          {traceId && (
            <span>
              trace{" "}
              <Link href={`/traces/${traceId}`} className="text-odin-cyan hover:underline">
                {traceId.slice(0, 12)}…
              </Link>
            </span>
          )}
          {causalChainId && (
            <span className="text-odin-muted">chain {causalChainId.slice(0, 12)}…</span>
          )}
        </div>
      )}

      <div className="relative space-y-0">
        <div className="absolute left-[11px] top-2 bottom-2 w-px bg-odin-border" />
        <AnimatePresence mode="popLayout">
          {filtered.map((entry, i) => {
            const id = `${entry.timestamp}-${entry.kind}-${i}`;
            const isOpen = expanded === id;
            const color = eventColor(entry.kind);
            return (
              <motion.div
                key={id}
                layout
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="relative pl-8"
              >
                <div
                  className="absolute left-1.5 top-3 h-2.5 w-2.5 rounded-full ring-2 ring-odin-bg"
                  style={{ backgroundColor: color }}
                />
                <button
                  type="button"
                  onClick={() => setExpanded(isOpen ? null : id)}
                  className="w-full rounded-lg border border-odin-border/50 bg-odin-panel/60 px-3 py-2 text-left transition-colors hover:border-odin-border"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className="rounded px-1.5 py-0.5 text-[10px] font-medium uppercase"
                      style={{ backgroundColor: `${color}22`, color }}
                    >
                      {entry.kind}
                    </span>
                    <span className="font-mono text-[10px] text-odin-muted">
                      {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : "—"}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-300">{entry.message}</p>
                  <p className="mt-0.5 text-[10px] text-odin-muted">
                    {entry.source}
                    {entry.task_id && ` · task ${entry.task_id.slice(0, 8)}`}
                  </p>
                </button>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <pre className="mt-1 max-h-48 overflow-auto rounded border border-odin-border bg-odin-bg p-2 font-mono text-[10px] text-slate-400">
                        {JSON.stringify(entry.payload ?? {}, null, 2)}
                      </pre>
                      {entry.trace_id && (
                        <Link
                          href={`/traces/${entry.trace_id}`}
                          className="mt-1 inline-flex items-center gap-1 text-[10px] text-odin-cyan"
                        >
                          View trace <ExternalLink className="h-3 w-3" />
                        </Link>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </AnimatePresence>
        {filtered.length === 0 && (
          <p className="py-8 text-center text-sm text-odin-muted">No events for this filter</p>
        )}
      </div>
    </div>
  );
}
