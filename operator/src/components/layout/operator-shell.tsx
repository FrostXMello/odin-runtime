"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Activity,
  Brain,
  GitBranch,
  Layers,
  MemoryStick,
  Radar,
  Route,
  Search,
  Terminal,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useOperatorStore } from "@/store/operator-store";
import { Badge } from "@/components/ui/badge";
import { useRuntimeStream } from "@/hooks/useRuntimeStream";
import { LiveIndicator, ConnectionHealthBadge } from "@/components/stream/live-indicator";
import { ActivityTicker } from "@/components/stream/activity-ticker";

const NAV = [
  { href: "/runtime", label: "Runtime", icon: Activity },
  { href: "/runtime/queues", label: "Queues", icon: Layers },
  { href: "/runtime/leases", label: "Leases", icon: GitBranch },
  { href: "/runtime/recovery", label: "Recovery", icon: Radar },
  { href: "/runtime/deadletters", label: "Deadletters", icon: Search },
  { href: "/runtime/topology", label: "Topology", icon: Brain },
  { href: "/runtime/workers", label: "Workers", icon: Terminal },
  { href: "/runtime/pools", label: "Pools", icon: Layers },
  { href: "/runtime/routing", label: "Routing", icon: Route },
  { href: "/runtime/planner", label: "Planner", icon: Brain },
  { href: "/runtime/tools", label: "Tools", icon: Terminal },
  { href: "/runtime/strategies", label: "Strategies", icon: Route },
  { href: "/runtime/cognition", label: "Cognition", icon: Brain },
  { href: "/runtime/learning", label: "Learning", icon: Brain },
  { href: "/runtime/optimization", label: "Optimization", icon: Radar },
  { href: "/runtime/failures", label: "Failures", icon: Search },
  { href: "/runtime/performance", label: "Performance", icon: Activity },
  { href: "/runtime/models", label: "Models", icon: Brain },
  { href: "/runtime/agents", label: "Agents", icon: Terminal },
  { href: "/runtime/reasoning", label: "Reasoning", icon: Route },
  { href: "/runtime/reflection", label: "Reflection", icon: Search },
  { href: "/runtime/resources", label: "Resources", icon: MemoryStick },
  { href: "/runtime/autonomy", label: "Autonomy", icon: Brain },
  { href: "/runtime/objectives", label: "Objectives", icon: Route },
  { href: "/runtime/research", label: "Research", icon: Search },
  { href: "/runtime/identity", label: "Identity", icon: Terminal },
  { href: "/runtime/environment", label: "Environment", icon: Radar },
  { href: "/runtime/safety", label: "Safety", icon: Activity },
  { href: "/runtime/perception", label: "Perception", icon: Radar },
  { href: "/runtime/desktop", label: "Desktop", icon: Terminal },
  { href: "/runtime/voice", label: "Voice", icon: Activity },
  { href: "/runtime/copilot", label: "Copilot", icon: Brain },
  { href: "/runtime/workspace", label: "Workspace", icon: MemoryStick },
  { href: "/runtime/collaboration", label: "Collaboration", icon: Route },
  { href: "/runtime/actions", label: "Actions", icon: Activity },
  { href: "/runtime/automation", label: "Automation", icon: Terminal },
  { href: "/runtime/browser", label: "Browser", icon: Radar },
  { href: "/runtime/workflows", label: "Workflows", icon: Route },
  { href: "/runtime/supervision", label: "Supervision", icon: Search },
  { href: "/runtime/overlay", label: "Overlay", icon: Layers },
  { href: "/runtime/knowledge", label: "Knowledge", icon: Brain },
  { href: "/runtime/research-fabric", label: "Research", icon: Search },
  { href: "/runtime/world-model", label: "World Model", icon: Radar },
  { href: "/runtime/beliefs", label: "Beliefs", icon: MemoryStick },
  { href: "/runtime/contradictions", label: "Contradictions", icon: Route },
  { href: "/runtime/trends", label: "Trends", icon: Activity },
  { href: "/runtime/sources", label: "Sources", icon: Terminal },
  { href: "/runtime/society", label: "Society", icon: Brain },
  { href: "/runtime/dialogues", label: "Dialogues", icon: Route },
  { href: "/runtime/delegation", label: "Delegation", icon: GitBranch },
  { href: "/runtime/expertise", label: "Expertise", icon: Radar },
  { href: "/runtime/federation", label: "Federation", icon: GitBranch },
  { href: "/runtime/world", label: "World", icon: Radar },
  { href: "/runtime/simulation", label: "Simulation", icon: Activity },
  { href: "/runtime/strategy", label: "Strategy", icon: Brain },
  { href: "/runtime/governance", label: "Governance", icon: Search },
  { href: "/runtime/federated-memory", label: "Fed Memory", icon: MemoryStick },
  { href: "/runtime/continuity", label: "Continuity", icon: MemoryStick },
  { href: "/runtime/background-cognition", label: "Background", icon: Activity },
  { href: "/runtime/evolution", label: "Evolution", icon: GitBranch },
  { href: "/runtime/economy", label: "Economy", icon: Terminal },
  { href: "/runtime/meta-reasoning", label: "Meta", icon: Brain },
  { href: "/runtime/operations", label: "Operations", icon: Route },
  { href: "/runtime/operator-profile", label: "Operator", icon: Search },
  { href: "/runtime/distributed-optimization", label: "Dist Opt", icon: Radar },
  { href: "/runtime/mission-cockpit", label: "Cockpit", icon: Route },
  { href: "/runtime/resources", label: "Resources", icon: Activity },
  { href: "/runtime/model-inspector", label: "Models", icon: Brain },
  { href: "/runtime/evaluation", label: "Benchmarks", icon: Terminal },
  { href: "/runtime/daemon", label: "Daemon", icon: MemoryStick },
  { href: "/runtime/stability", label: "Stability", icon: Activity },
  { href: "/runtime/recovery", label: "Recovery", icon: Radar },
  { href: "/runtime/daemon-health", label: "Daemon Health", icon: MemoryStick },
  { href: "/runtime/automation-live", label: "Automation", icon: Terminal },
  { href: "/runtime/action-validation", label: "Validation", icon: Search },
  { href: "/runtime/self-healing", label: "Self-Heal", icon: GitBranch },
  { href: "/runtime/resource-survival", label: "Survival", icon: Activity },
  { href: "/runtime/session-continuity", label: "Continuity", icon: Route },
  { href: "/runtime/projects", label: "Projects", icon: Route },
  { href: "/runtime/workspaces", label: "Workspaces", icon: MemoryStick },
  { href: "/runtime/repositories", label: "Repos", icon: GitBranch },
  { href: "/runtime/developer", label: "Developer", icon: Terminal },
  { href: "/runtime/knowledge-workspace", label: "Knowledge", icon: Brain },
  { href: "/runtime/tasks", label: "Tasks", icon: Route },
  { href: "/runtime/focus", label: "Focus", icon: Activity },
  { href: "/runtime/briefings", label: "Briefings", icon: Search },
  { href: "/runtime/search", label: "Search", icon: Search },
  { href: "/runtime/storage", label: "Storage", icon: MemoryStick },
  { href: "/missions", label: "Missions", icon: Route },
  { href: "/executions", label: "Executions", icon: Terminal },
  { href: "/graph", label: "Signal Graph", icon: GitBranch },
  { href: "/diagnostics", label: "Diagnostics", icon: Radar },
  { href: "/memory", label: "Memory Audit", icon: MemoryStick },
];

export function OperatorShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { pollIntervalMs, liveRefresh, setPollInterval, setLiveRefresh } = useOperatorStore();
  useRuntimeStream(liveRefresh);

  return (
    <div className="flex min-h-screen bg-odin-bg text-slate-200">
      <aside className="flex w-56 shrink-0 flex-col border-r border-odin-border bg-odin-panel/90">
        <div className="border-b border-odin-border px-4 py-5">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-odin-accent to-odin-violet shadow-glow">
              <Layers className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-xs font-bold tracking-[0.2em] text-odin-cyan">ODIN</p>
              <p className="text-[10px] text-odin-muted">Operator Console</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-0.5 p-2">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-odin-accent/15 text-odin-cyan"
                    : "text-slate-400 hover:bg-odin-border/40 hover:text-slate-200"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {label}
              </Link>
            );
          })}
          <Link
            href="/traces"
            className={cn(
              "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname.startsWith("/traces")
                ? "bg-odin-accent/15 text-odin-cyan"
                : "text-slate-400 hover:bg-odin-border/40 hover:text-slate-200"
            )}
          >
            <Search className="h-4 w-4" />
            Traces
          </Link>
        </nav>
        <div className="border-t border-odin-border p-3 space-y-2">
          <label className="flex items-center justify-between text-[10px] text-odin-muted">
            <span>Live refresh</span>
            <input
              type="checkbox"
              checked={liveRefresh}
              onChange={(e) => setLiveRefresh(e.target.checked)}
              className="accent-odin-accent"
            />
          </label>
          <label className="block text-[10px] text-odin-muted">
            Poll {liveRefresh ? `${pollIntervalMs / 1000}s` : "off"}
            <input
              type="range"
              min={1000}
              max={10000}
              step={500}
              value={pollIntervalMs}
              disabled={!liveRefresh}
              onChange={(e) => setPollInterval(Number(e.target.value))}
              className="mt-1 w-full accent-odin-accent"
            />
          </label>
          <div className="space-y-1">
            <LiveIndicator channel="runtime" />
            <ConnectionHealthBadge channel="runtime" />
          </div>
        </div>
      </aside>
      <main className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-12 items-center justify-between border-b border-odin-border bg-odin-panel/50 px-6 backdrop-blur-md">
          <motion.h1
            key={pathname}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-sm font-medium text-slate-300"
          >
            {NAV.find((n) => pathname.startsWith(n.href))?.label ?? "Trace Explorer"}
          </motion.h1>
          <div className="flex items-center gap-3">
            <LiveIndicator channel="runtime" />
            <p className="font-mono text-[10px] text-odin-muted">REST fallback · WS stream</p>
          </div>
        </header>
        <ActivityTicker />
        <div className="flex-1 overflow-auto p-6">{children}</div>
      </main>
    </div>
  );
}
