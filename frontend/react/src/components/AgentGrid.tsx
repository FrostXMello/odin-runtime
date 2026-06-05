import { motion } from "framer-motion";

interface Agent {
  id: string;
  name: string;
  description: string;
  state: string;
}

export function AgentGrid({ agents }: { agents: Agent[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {agents.map((agent, i) => (
        <motion.div
          key={agent.id}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className="rounded-xl border border-odin-border bg-odin-panel p-4"
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-odin-accent">{agent.name}</h3>
            <span
              className={`text-xs px-2 py-0.5 rounded-full ${
                agent.state === "idle"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-amber-500/20 text-amber-400"
              }`}
            >
              {agent.state}
            </span>
          </div>
          <p className="text-sm text-odin-muted">{agent.description}</p>
          <p className="text-xs font-mono mt-3 text-slate-500">{agent.id}</p>
        </motion.div>
      ))}
    </div>
  );
}
