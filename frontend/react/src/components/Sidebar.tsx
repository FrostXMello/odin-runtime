import { motion } from "framer-motion";

const NAV = [
  { id: "command", label: "Command Center" },
  { id: "kernel", label: "Cognitive Kernel" },
  { id: "conversation", label: "Conversation" },
  { id: "live-desktop", label: "Live Desktop" },
  { id: "workspace-intel", label: "Workspace Intel" },
  { id: "attention", label: "Cognitive Attention" },
  { id: "resilience", label: "Resilience" },
  { id: "agent-society", label: "Agent Society" },
  { id: "trust", label: "Trust & Security" },
  { id: "compute-runtime", label: "Compute Runtime" },
  { id: "memory-timeline", label: "Memory Timeline" },
  { id: "context-timeline", label: "Context Timeline" },
  { id: "cognitive-stream", label: "Cognitive Stream" },
  { id: "recommendations", label: "Recommendations" },
  { id: "execution-intel", label: "Execution Intel" },
  { id: "collaboration", label: "Collaboration" },
  { id: "local-models", label: "Local Models" },
  { id: "cognition", label: "Cognition Stream" },
  { id: "workflows", label: "Workflow Graph" },
  { id: "runtime", label: "Runtime Health" },
  { id: "browser", label: "Browser Session" },
  { id: "watchers", label: "Background Monitors" },
  { id: "agents", label: "Agent Console" },
  { id: "tasks", label: "Task Queue" },
  { id: "events", label: "Event Stream" },
  { id: "permissions", label: "Permissions" },
  { id: "memory", label: "Memory" },
  { id: "knowledge", label: "Knowledge Graph" },
  { id: "reflection", label: "Reflection" },
  { id: "voice", label: "Voice Console" },
  { id: "sandbox", label: "Sandbox" },
  { id: "logs", label: "Logs" },
  { id: "tools", label: "Tools" },
];

interface SidebarProps {
  active: string;
  onNavigate: (id: string) => void;
}

export function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="w-56 border-r border-odin-border bg-odin-panel/50 flex flex-col">
      <div className="p-5 border-b border-odin-border">
        <motion.h1
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xl font-bold tracking-widest text-odin-gold"
        >
          ODIN
        </motion.h1>
        <p className="text-xs text-odin-muted mt-1">AI Operations</p>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
              active === item.id
                ? "bg-odin-accent/20 text-odin-accent"
                : "text-odin-muted hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
