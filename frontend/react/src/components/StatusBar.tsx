import { motion } from "framer-motion";

interface StatusBarProps {
  connected: boolean;
  running: boolean;
  activeTasks: number;
}

export function StatusBar({ connected, running, activeTasks }: StatusBarProps) {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-8 border-t border-odin-border bg-odin-panel/80 flex items-center px-4 gap-6 text-xs font-mono"
    >
      <span className="flex items-center gap-2">
        <span
          className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-400" : "bg-red-500"}`}
        />
        {connected ? "Backend connected" : "Backend offline"}
      </span>
      <span className="text-odin-muted">|</span>
      <span>Orchestrator: {running ? "running" : "stopped"}</span>
      <span className="text-odin-muted">|</span>
      <span>Active tasks: {activeTasks}</span>
    </motion.footer>
  );
}
